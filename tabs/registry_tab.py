#!/usr/bin/env python3
"""registry_tab.py -- Registry tab: every issued key across all apps with
filtering, copy, edit name/notes, revoke/re-activate, and re-issue."""
from __future__ import annotations
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                               QTableWidget, QTableWidgetItem, QComboBox,
                               QLineEdit, QPushButton, QLabel, QMessageBox,
                               QApplication, QInputDialog)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

import keycrypto
from helpers import entry_state

COLS = ["App", "Tier", "Licensee", "Expiry", "Status", "Issued", "Notes"]

# Row tints for stale keys (chosen to read on the dark 3D theme).
_RED   = QColor("#7a2e2e")   # key no longer verifies against current app key
_AMBER = QColor("#7a5b1e")   # edited after minting; still valid but out of sync
_STALE_TIP = {
    "invalid": "Key no longer verifies against this app's current key "
               "(keypair re-generated or app changed). Re-issue to fix.",
    "edited":  "Row edited after minting — the key still carries the old "
               "details. Re-issue to update the key.",
}


class RegistryTab(QWidget):
    def __init__(self, keystore, on_change):
        super().__init__()
        self.ks = keystore
        self.on_change = on_change
        self._rows = []          # parallel list of registry entries shown
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        root = QVBoxLayout(self)
        box = QGroupBox("Issued keys")
        v = QVBoxLayout(box)

        f = QHBoxLayout()
        self.app_f = QComboBox(); self.app_f.currentIndexChanged.connect(self._fill)
        self.tier_f = QComboBox(); self.tier_f.addItem("All tiers", "")
        for t in keycrypto.TIERS:
            self.tier_f.addItem(t, t)
        self.tier_f.currentIndexChanged.connect(self._fill)
        self.name_f = QLineEdit(); self.name_f.setPlaceholderText("filter by name")
        self.name_f.textChanged.connect(self._fill)
        f.addWidget(QLabel("App:")); f.addWidget(self.app_f)
        f.addWidget(self.tier_f); f.addWidget(self.name_f)
        v.addLayout(f)

        self.table = QTableWidget(0, len(COLS))
        self.table.setHorizontalHeaderLabels(COLS)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)
        v.addWidget(self.table)

        b = QHBoxLayout()
        for label, slot in (("Copy key", self._copy), ("Edit name", self._edit_name),
                            ("Edit notes", self._edit_notes),
                            ("Toggle revoked", self._toggle), ("Re-issue", self._reissue),
                            ("Delete", self._delete)):
            btn = QPushButton(label); btn.clicked.connect(slot); b.addWidget(btn)
        v.addLayout(b)
        root.addWidget(box)

    def refresh(self):
        cur = self.app_f.currentData()
        self.app_f.blockSignals(True)
        self.app_f.clear(); self.app_f.addItem("All apps", "")
        for app in self.ks.apps:
            self.app_f.addItem(app["id"], app["id"])
        i = self.app_f.findData(cur)
        if i >= 0:
            self.app_f.setCurrentIndex(i)
        self.app_f.blockSignals(False)
        self._fill()

    def _fill(self, *_):
        app_f = self.app_f.currentData() or ""
        tier_f = self.tier_f.currentData() or ""
        name_f = self.name_f.text().strip().lower()
        self._rows = []
        for e in self.ks.registry:
            if app_f and e["app_id"] != app_f:
                continue
            if tier_f and e["tier"] != tier_f:
                continue
            if name_f and name_f not in e["name"].lower():
                continue
            self._rows.append(e)

        self.table.setRowCount(len(self._rows))
        for r, e in enumerate(self._rows):
            state = entry_state(e, self.ks)          # "ok" | "invalid" | "edited"
            status_txt = e["status"]
            if state != "ok" and e["status"] != "revoked":
                status_txt += "  ⚠ re-mint"
            vals = [e["app_id"], e["tier"], e["name"],
                    "never" if e["exp"] == "0" else e["exp"],
                    status_txt, e["issued_at"][:10], e.get("notes", "")]
            for c, val in enumerate(vals):
                item = QTableWidgetItem(val)
                if e["status"] == "revoked":
                    item.setForeground(Qt.gray)
                elif state == "invalid":
                    item.setBackground(_RED);   item.setToolTip(_STALE_TIP["invalid"])
                elif state == "edited":
                    item.setBackground(_AMBER); item.setToolTip(_STALE_TIP["edited"])
                self.table.setItem(r, c, item)

    def _selected(self):
        r = self.table.currentRow()
        return self._rows[r] if 0 <= r < len(self._rows) else None

    def _copy(self):
        e = self._selected()
        if e:
            QApplication.clipboard().setText(e["key"])

    def _edit_name(self):
        e = self._selected()
        if not e:
            return
        name, ok = QInputDialog.getText(self, "Edit name", "Licensee:", text=e["name"])
        if ok:
            self.ks.update_entry(e["key"], name=name.strip()); self.ks.save()
            self._fill(); self.on_change()

    def _edit_notes(self):
        e = self._selected()
        if not e:
            return
        notes, ok = QInputDialog.getMultiLineText(self, "Edit notes", "Notes:",
                                                  text=e.get("notes", ""))
        if ok:
            self.ks.update_entry(e["key"], notes=notes); self.ks.save()
            self._fill()

    def _toggle(self):
        e = self._selected()
        if not e:
            return
        new = "active" if e["status"] == "revoked" else "revoked"
        if new == "revoked":
            QMessageBox.information(self, "Revoke",
                "Offline keys can't be cryptographically revoked. This flag is "
                "for your tracking only — the key still verifies in the app.")
        self.ks.set_status(e["key"], new); self.ks.save()
        self._fill()

    def _reissue(self):
        e = self._selected()
        if not e:
            return
        app = self.ks.get_app(e["app_id"])
        if not app or not app.get("keypair"):
            QMessageBox.warning(self, "Re-issue", "App keypair missing."); return
        # Sign a fresh key from the row's CURRENT tier/name/exp (so an edited
        # name is baked in) with the app's CURRENT keypair, then swap it into
        # this same row — clears any red/amber stale flag in place.
        payload = keycrypto.make_payload(e["tier"], e["name"], e["exp"])
        key = keycrypto.sign_payload(payload, keycrypto.obj_to_key(app["keypair"]))
        parsed = keycrypto.parse_payload(payload)
        self.ks.reissue_entry(e["key"], key, parsed["nonce"])
        self.ks.save()
        QApplication.clipboard().setText(key)
        QMessageBox.information(self, "Re-issue",
                                "Key re-minted in place and copied to clipboard.")
        self._fill(); self.on_change()

    def _delete(self):
        e = self._selected()
        if not e:
            return
        if QMessageBox.warning(
                self, "Delete key",
                f'Delete the {e["tier"]} key for "{e["name"]}" from the registry?\n\n'
                "This removes it from your local record only. It does NOT disable a "
                "key already in use (offline keys can't be revoked).",
                QMessageBox.Yes | QMessageBox.No) != QMessageBox.Yes:
            return
        self.ks.delete_entry(e["key"])
        self.ks.save()
        self._fill()
        self.on_change()
