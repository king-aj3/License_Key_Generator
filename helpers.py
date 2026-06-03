#!/usr/bin/env python3
"""helpers.py -- tiny shared utilities used by more than one tab."""
from __future__ import annotations
import hashlib

import keycrypto


def fingerprint(keypair_obj: dict | None) -> str:
    """Short, stable id for a key so you can confirm which key an app is on.
    Derived from the public modulus n only (safe to display)."""
    if not keypair_obj:
        return "—"
    digest = hashlib.sha256(keypair_obj["n"].encode()).hexdigest()[:16].upper()
    return ":".join(digest[i:i + 4] for i in range(0, 16, 4))


def pubkey_block(keypair_obj: dict) -> str:
    """Ready-to-paste public-key constant block for embedding in an app."""
    return (f'_PUBKEY_N = "{keypair_obj["n"]}"\n'
            f'_PUBKEY_E = {keypair_obj["e"]}')


def entry_state(entry: dict, ks) -> str:
    """Staleness of a registry entry relative to its app's CURRENT key.

    Returns:
      "ok"      - key verifies and its baked-in fields match the stored record.
      "invalid" - key no longer verifies against the app's current public key
                  (keypair was re-generated, or the app is gone). RED.
      "edited"  - key still verifies, but the row's tier/name/exp no longer
                  match what is baked into the key (row edited after minting,
                  not re-minted). AMBER.
    """
    app = ks.get_app(entry.get("app_id", ""))
    if not app or not app.get("keypair"):
        return "invalid"
    pub = keycrypto.obj_to_key({"n": app["keypair"]["n"], "e": app["keypair"]["e"]})
    payload = keycrypto.verify_key(entry["key"], pub)
    if payload is None:
        return "invalid"
    p = keycrypto.parse_payload(payload)
    if (p.get("tier") != entry.get("tier")
            or p.get("name") != entry.get("name")
            or p.get("exp") != entry.get("exp")):
        return "edited"
    return "ok"
