#!/usr/bin/env python3
"""mint_tab.py -- Mint tab: pick app + tier + licensee + expiry, sign a key
with that app's private key, show it for copy, append it to the registry."""
from __future__ import annotations
from PySide6.QtWidgets import (QWidget, QFormLayout, QVBoxLayout, QGroupBox,
                               QComboBox, QLineEdit, QPushButton, QPlainTextEdit,
                               QCheckBox, QDateEdit, QHBoxLayout, QMessageBox,
                               QApplication)
from PySide6.QtCore import QDate

import keycrypto


class MintTab(QWidget):
    def __init__(self, keystore, on_change):
        super().__init__()
        self.ks = keystore
        self.on_change = on_change
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        root = QVBoxLayout(self)
        box = QGroupBox("Mint a license key")
        form = QFormLayout(box)

        self.app_combo = QComboBox()
        self.tier_combo = QComboBox(); self.tier_combo.addItems(keycrypto.TIERS)
        self.name_edit = QLineEdit(); self.name_edit.setPlaceholderText("licensee name")

        exp_row = QHBoxLayout()
        self.never_chk = QCheckBox("Never expires"); self.never_chk.setChecked(True)
        self.never_chk.toggled.connect(lambda v: self.date_edit.setEnabled(not v))
        self.date_edit = QDateEdit(); self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate().addYears(1))
        self.date_edit.setEnabled(False)
        exp_row.addWidget(self.never_chk); exp_row.addWidget(self.date_edit)

        form.addRow("App:", self.app_combo)
        form.addRow("Tier:", self.tier_combo)
        form.addRow("Licensee:", self.name_edit)
        form.addRow("Expiry:", self._wrap(exp_row))

        self.mint_btn = QPushButton("Mint key")
        self.mint_btn.clicked.connect(self._mint)
        form.addRow(self.mint_btn)

        self.out = QPlainTextEdit(); self.out.setReadOnly(True)
        self.out.setFixedHeight(70)
        form.addRow("Key:", self.out)
        self.copy_btn = QPushButton("Copy key"); self.copy_btn.setEnabled(False)
        self.copy_btn.clicked.connect(
            lambda: QApplication.clipboard().setText(self.out.toPlainText()))
        form.addRow(self.copy_btn)

        root.addWidget(box); root.addStretch(1)

    @staticmethod
    def _wrap(layout):
        w = QWidget(); w.setLayout(layout); return w

    def refresh(self):
        cur = self.app_combo.currentData()
        self.app_combo.clear()
        for app in self.ks.apps:
            self.app_combo.addItem(f'{app["id"]} — {app["display_name"]}', app["id"])
        if cur:
            i = self.app_combo.findData(cur)
            if i >= 0:
                self.app_combo.setCurrentIndex(i)

    def _mint(self):
        app_id = self.app_combo.currentData()
        app = self.ks.get_app(app_id) if app_id else None
        if not app:
            QMessageBox.warning(self, "Mint", "No app selected."); return
        if not app.get("keypair"):
            QMessageBox.warning(self, "Mint",
                                "This app has no keypair yet. Generate one in the Apps tab.")
            return
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Mint", "Licensee name is required."); return

        exp = "0" if self.never_chk.isChecked() else self.date_edit.date().toString("yyyy-MM-dd")
        tier = self.tier_combo.currentText()
        payload = keycrypto.make_payload(tier, name, exp)
        priv = keycrypto.obj_to_key(app["keypair"])
        key = keycrypto.sign_payload(payload, priv)
        parsed = keycrypto.parse_payload(payload)

        self.ks.add_entry(app_id, tier, parsed["name"], exp, parsed["nonce"], key)
        self.ks.save()
        self.out.setPlainText(key)
        self.copy_btn.setEnabled(True)
        self.on_change()
