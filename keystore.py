#!/usr/bin/env python3
"""keystore.py -- on-disk store for managed apps and the issued-key registry.

The keystore is the crown jewels: it holds every app's PRIVATE key. It lives in
a per-user app-data dir (never the repo, never a build) in a single JSON file
that is permission-locked (POSIX chmod 600 / Windows icacls) on every save.

Schema:
  {
    "apps":     [{"id", "display_name", "keypair": {"n","e","d"} | None}],
    "registry": [{"app_id","tier","name","exp","nonce","key",
                  "issued_at","status","notes"}]
  }
"""
from __future__ import annotations
import json, os, sys, shutil, subprocess, tempfile
from datetime import datetime, timezone

APP_DIR_NAME = ".ajj3_license_manager"
STORE_FILENAME = "keystore.json"


def default_store_dir() -> str:
    return os.path.join(os.path.expanduser("~"), APP_DIR_NAME)


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _lock_file(path: str) -> None:
    """Best-effort: restrict the file to the current user only."""
    try:
        if os.name == "nt":
            user = os.environ.get("USERNAME", "")
            subprocess.run(["icacls", path, "/inheritance:r"],
                           capture_output=True, check=False)
            if user:
                subprocess.run(["icacls", path, "/grant:r", f"{user}:F"],
                               capture_output=True, check=False)
        else:
            os.chmod(path, 0o600)
    except Exception:
        pass  # locking is hardening, not correctness — never block a save


class Keystore:
    def __init__(self, store_dir: str | None = None):
        self.dir = store_dir or default_store_dir()
        self.path = os.path.join(self.dir, STORE_FILENAME)
        self.data = {"apps": [], "registry": []}

    # ---- persistence -----------------------------------------------------
    def load(self) -> "Keystore":
        if os.path.exists(self.path):
            with open(self.path, "r", encoding="utf-8") as fh:
                self.data = json.load(fh)
        self.data.setdefault("apps", [])
        self.data.setdefault("registry", [])
        return self

    def save(self) -> None:
        os.makedirs(self.dir, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=self.dir, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                json.dump(self.data, fh, indent=2)
            os.replace(tmp, self.path)
        finally:
            if os.path.exists(tmp):
                os.remove(tmp)
        _lock_file(self.path)

    # ---- apps ------------------------------------------------------------
    @property
    def apps(self) -> list:
        return self.data["apps"]

    def get_app(self, app_id: str) -> dict | None:
        return next((a for a in self.apps if a["id"] == app_id), None)

    def add_app(self, app_id: str, display_name: str) -> dict:
        app_id = app_id.strip().upper()
        if not app_id:
            raise ValueError("App id is required.")
        if self.get_app(app_id):
            raise ValueError(f"App id '{app_id}' already exists.")
        app = {"id": app_id, "display_name": display_name.strip() or app_id,
               "keypair": None}
        self.apps.append(app)
        return app

    def rename_app(self, app_id: str, display_name: str) -> None:
        app = self.get_app(app_id)
        if not app:
            raise ValueError(f"No app '{app_id}'.")
        app["display_name"] = display_name.strip() or app_id

    def set_keypair(self, app_id: str, keypair_obj: dict) -> None:
        """keypair_obj = priv_to_obj(...) hex dict {n,e,d}."""
        app = self.get_app(app_id)
        if not app:
            raise ValueError(f"No app '{app_id}'.")
        app["keypair"] = keypair_obj

    # ---- registry --------------------------------------------------------
    @property
    def registry(self) -> list:
        return self.data["registry"]

    def add_entry(self, app_id, tier, name, exp, nonce, key, notes="") -> dict:
        entry = {"app_id": app_id, "tier": tier, "name": name, "exp": exp,
                 "nonce": nonce, "key": key, "issued_at": _now_iso(),
                 "status": "active", "notes": notes}
        self.registry.append(entry)
        return entry

    def find_entry(self, key: str) -> dict | None:
        return next((e for e in self.registry if e["key"] == key), None)

    def set_status(self, key: str, status: str) -> None:
        e = self.find_entry(key)
        if e:
            e["status"] = status

    def update_entry(self, key: str, name=None, notes=None) -> None:
        e = self.find_entry(key)
        if not e:
            return
        if name is not None:
            e["name"] = name
        if notes is not None:
            e["notes"] = notes

    def delete_entry(self, key: str) -> None:
        """Remove a registry entry. Local record only — does not disable any
        key already in use (offline keys can't be revoked)."""
        self.data["registry"] = [e for e in self.registry if e["key"] != key]

    def reissue_entry(self, key: str, new_key: str, new_nonce: str) -> None:
        """Replace a row's key in place: swap in the freshly minted key/nonce,
        stamp issued_at now, and reset status to active. Keeps list position
        (and the row's tier/name/exp/notes) so re-minting doesn't pile up rows."""
        e = self.find_entry(key)
        if not e:
            return
        e["key"] = new_key
        e["nonce"] = new_nonce
        e["issued_at"] = _now_iso()
        e["status"] = "active"

    def delete_app(self, app_id: str) -> None:
        """Remove an app, its keypair, and every registry entry issued for it."""
        self.data["apps"] = [a for a in self.apps if a["id"] != app_id]
        self.data["registry"] = [e for e in self.registry if e["app_id"] != app_id]

    # ---- backup / restore ------------------------------------------------
    def backup(self, dest_path: str) -> None:
        if not os.path.exists(self.path):
            self.save()
        shutil.copy2(self.path, dest_path)

    def restore(self, src_path: str) -> None:
        with open(src_path, "r", encoding="utf-8") as fh:
            incoming = json.load(fh)
        if "apps" not in incoming or "registry" not in incoming:
            raise ValueError("File is not a valid keystore backup.")
        self.data = incoming
        self.save()
