#!/usr/bin/env python3
"""verify_tab.py -- Verify tab: paste a key + pick app, run verify_key against
that app's public key, show the parsed tier/name/exp (debug/confirm)."""
from __future__ import annotations
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QGroupBox,
                               QComboBox, QPlainTextEdit, QPushButton, QLabel)

import keycrypto


class VerifyTab(QWidget):
    def __init__(self, keystore, on_change=None):
        super().__init__()
        self.ks = keystore
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        root = QVBoxLayout(self)
        box = QGroupBox("Verify a key")
        form = QFormLayout(box)
        self.app_combo = QComboBox()
        self.key_in = QPlainTextEdit(); self.key_in.setFixedHeight(70)
        self.key_in.setPlaceholderText("paste AJK1.… key here")
        btn = QPushButton("Verify"); btn.clicked.connect(self._verify)
        self.result = QLabel("—"); self.result.setWordWrap(True)
        form.addRow("App:", self.app_combo)
        form.addRow("Key:", self.key_in)
        form.addRow(btn)
        form.addRow("Result:", self.result)
        root.addWidget(box); root.addStretch(1)

    def refresh(self):
        cur = self.app_combo.currentData()
        self.app_combo.clear()
        for app in self.ks.apps:
            self.app_combo.addItem(f'{app["id"]} — {app["display_name"]}', app["id"])
        if cur:
            i = self.app_combo.findData(cur)
            if i >= 0:
                self.app_combo.setCurrentIndex(i)

    def _verify(self):
        app = self.ks.get_app(self.app_combo.currentData() or "")
        if not app or not app.get("keypair"):
            self.result.setText("<b>App has no keypair.</b>"); return
        pub = keycrypto.obj_to_key({"n": app["keypair"]["n"], "e": app["keypair"]["e"]})
        payload = keycrypto.verify_key(self.key_in.toPlainText(), pub)
        if not payload:
            self.result.setText('<b style="color:#e06c6c">INVALID</b> for this app.')
            return
        p = keycrypto.parse_payload(payload)
        self.result.setText(
            f'<b style="color:#6cc06c">VALID</b><br>'
            f'Tier: {p["tier"]}<br>Name: {p["name"]}<br>'
            f'Expiry: {"never" if p["exp"] == "0" else p["exp"]}<br>'
            f'Nonce: {p["nonce"]}')
