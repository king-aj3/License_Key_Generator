#!/usr/bin/env python3
"""apps_tab.py -- Apps tab: add/rename apps, generate a one-time keypair,
export the public key as a paste-ready constant block, show a fingerprint."""
from __future__ import annotations
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QGroupBox,
                               QListWidget, QListWidgetItem, QPushButton,
                               QLineEdit, QLabel, QPlainTextEdit, QMessageBox,
                               QInputDialog)

import keycrypto
from helpers import fingerprint, pubkey_block, entry_state


class AppsTab(QWidget):
    def __init__(self, keystore, on_change):
        super().__init__()
        self.ks = keystore
        self.on_change = on_change          # notify other tabs to refresh
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        root = QHBoxLayout(self)

        left = QGroupBox("Managed apps")
        lv = QVBoxLayout(left)
        self.app_list = QListWidget()
        self.app_list.currentItemChanged.connect(self._show_selected)
        lv.addWidget(self.app_list)

        add_row = QHBoxLayout()
        self.new_id = QLineEdit(); self.new_id.setPlaceholderText("id e.g. MLLM")
        self.new_name = QLineEdit(); self.new_name.setPlaceholderText("display name")
        add_btn = QPushButton("Add"); add_btn.clicked.connect(self._add_app)
        add_row.addWidget(self.new_id); add_row.addWidget(self.new_name)
        add_row.addWidget(add_btn)
        lv.addLayout(add_row)
        root.addWidget(left, 1)

        right = QGroupBox("App details")
        rv = QVBoxLayout(right)
        self.detail = QLabel("Select an app."); self.detail.setWordWrap(True)
        rv.addWidget(self.detail)

        btn_row = QHBoxLayout()
        self.rename_btn = QPushButton("Rename"); self.rename_btn.clicked.connect(self._rename)
        self.gen_btn = QPushButton("Generate keypair"); self.gen_btn.clicked.connect(self._gen)
        self.delete_btn = QPushButton("Delete app"); self.delete_btn.clicked.connect(self._delete_app)
        btn_row.addWidget(self.rename_btn); btn_row.addWidget(self.gen_btn)
        btn_row.addWidget(self.delete_btn)
        rv.addLayout(btn_row)

        rv.addWidget(QLabel("Public key to embed in the app:"))
        self.pub_box = QPlainTextEdit(); self.pub_box.setReadOnly(True)
        self.pub_box.setFixedHeight(90)
        rv.addWidget(self.pub_box)
        self.copy_btn = QPushButton("Copy public-key block")
        self.copy_btn.clicked.connect(self._copy_pub)
        rv.addWidget(self.copy_btn)
        root.addWidget(right, 2)

    # ---- data ------------------------------------------------------------
    def refresh(self):
        cur = self._current_id()
        self.app_list.clear()
        for app in self.ks.apps:
            item = QListWidgetItem(f'{app["id"]}  —  {app["display_name"]}')
            item.setData(0x0100, app["id"])  # Qt.UserRole
            self.app_list.addItem(item)
            if app["id"] == cur:
                self.app_list.setCurrentItem(item)
        self._show_selected()

    def _current_id(self):
        item = self.app_list.currentItem()
        return item.data(0x0100) if item else None

    def _show_selected(self, *_):
        app = self.ks.get_app(self._current_id() or "")
        has = bool(app)
        self.rename_btn.setEnabled(has)
        self.gen_btn.setEnabled(has)
        self.delete_btn.setEnabled(has)
        self.copy_btn.setEnabled(bool(app and app.get("keypair")))
        if not app:
            self.detail.setText("Select an app.")
            self.pub_box.setPlainText("")
            return
        kp = app.get("keypair")
        stale = sum(1 for e in self.ks.registry
                    if e["app_id"] == app["id"] and entry_state(e, self.ks) != "ok")
        badge = (f'<br><span style="color:#d9a441">⚠ {stale} key(s) need '
                 f're-mint — see Registry</span>') if stale else ""
        self.detail.setText(
            f'<b>{app["id"]}</b> — {app["display_name"]}<br>'
            f'Keypair: {"set" if kp else "not generated"}<br>'
            f'Fingerprint: <code>{fingerprint(kp)}</code>{badge}')
        self.gen_btn.setText("Re-generate keypair" if kp else "Generate keypair")
        self.pub_box.setPlainText(
            pubkey_block({"n": kp["n"], "e": kp["e"]}) if kp else "")

    # ---- actions ---------------------------------------------------------
    def _add_app(self):
        try:
            app = self.ks.add_app(self.new_id.text(), self.new_name.text())
            self.ks.save()
            self.new_id.clear(); self.new_name.clear()
            self.refresh()
            self.on_change()
            self._select(app["id"])
        except ValueError as e:
            QMessageBox.warning(self, "Add app", str(e))

    def _rename(self):
        app_id = self._current_id()
        if not app_id:
            return
        name, ok = QInputDialog.getText(self, "Rename app", "Display name:",
                                        text=self.ks.get_app(app_id)["display_name"])
        if ok:
            self.ks.rename_app(app_id, name); self.ks.save()
            self.refresh(); self.on_change()

    def _gen(self):
        app_id = self._current_id()
        app = self.ks.get_app(app_id)
        if not app:
            return
        if app.get("keypair"):
            warn = ("This app already has a keypair. Re-generating creates a NEW "
                    "key — every license already issued for this app will STOP "
                    "verifying and you must re-embed the new public key.\n\nContinue?")
            if QMessageBox.warning(self, "Re-generate keypair", warn,
                                   QMessageBox.Yes | QMessageBox.No) != QMessageBox.Yes:
                return
        priv = keycrypto.generate_keypair()
        self.ks.set_keypair(app_id, keycrypto.priv_to_obj(priv))
        self.ks.save()
        self._show_selected()
        self.on_change()

    def _delete_app(self):
        app_id = self._current_id()
        app = self.ks.get_app(app_id)
        if not app:
            return
        n = sum(1 for e in self.ks.registry if e["app_id"] == app_id)
        msg = f'Delete app "{app["id"]}" — {app["display_name"]}?\n\n'
        if app.get("keypair"):
            msg += ("Its private key will be permanently destroyed. Any build of this "
                    "app that embedded the matching public key will then accept NO key "
                    "you can mint here.\n\n")
        if n:
            msg += f"This will also remove {n} issued key(s) for it from the registry.\n\n"
        msg += "This cannot be undone."
        if QMessageBox.warning(self, "Delete app", msg,
                               QMessageBox.Yes | QMessageBox.No) != QMessageBox.Yes:
            return
        self.ks.delete_app(app_id)
        self.ks.save()
        self.refresh()
        self.on_change()

    def _copy_pub(self):
        from PySide6.QtWidgets import QApplication
        QApplication.clipboard().setText(self.pub_box.toPlainText())

    def _select(self, app_id):
        for i in range(self.app_list.count()):
            if self.app_list.item(i).data(0x0100) == app_id:
                self.app_list.setCurrentRow(i); return
