#!/usr/bin/env python3
"""AJJ3 License Manager -- the only place that mints license keys for the
AJJ3 apps. Holds every app's private key and signs keys offline; the apps
embed only their public key and verify. Pure stdlib crypto + PySide6.
"""
from __future__ import annotations
import os
import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QApplication, QMainWindow, QTabWidget,
                               QFileDialog, QMessageBox)

from keystore import Keystore
from ui_theme import STYLESHEET
from tabs.apps_tab import AppsTab
from tabs.mint_tab import MintTab
from tabs.registry_tab import RegistryTab
from tabs.verify_tab import VerifyTab

APP_NAME = "AJJ3 License Manager"
APP_VERSION = "1.0.0"


def _app_icon() -> QIcon:
    """Window/taskbar icon, picking the right file per OS. Resolved relative
    to this file so it works from source and from a Nuitka build (icons ship
    in assets/ via pyproject data_files)."""
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
    if sys.platform.startswith("win"):
        name = "icon.ico"
    elif sys.platform == "darwin":
        name = "icon.icns"
    else:  # Linux / other
        name = "icon-256.png"
    path = os.path.join(base, name)
    if not os.path.exists(path):          # PNG renders on every platform
        path = os.path.join(base, "icon-256.png")
    return QIcon(path)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(880, 560)
        self.ks = Keystore().load()

        self.tabs = QTabWidget()
        self.apps_tab = AppsTab(self.ks, self._refresh_all)
        self.mint_tab = MintTab(self.ks, self._refresh_all)
        self.registry_tab = RegistryTab(self.ks, self._refresh_all)
        self.verify_tab = VerifyTab(self.ks)
        self.tabs.addTab(self.apps_tab, "Apps")
        self.tabs.addTab(self.mint_tab, "Mint")
        self.tabs.addTab(self.registry_tab, "Registry")
        self.tabs.addTab(self.verify_tab, "Verify")
        self.setCentralWidget(self.tabs)

        self._build_menu()

    def _build_menu(self):
        m = self.menuBar().addMenu("&Keystore")
        m.addAction("Backup…", self._backup)
        m.addAction("Restore…", self._restore)
        m.addSeparator()
        m.addAction("About", self._about)

    def _refresh_all(self):
        self.apps_tab.refresh()
        self.mint_tab.refresh()
        self.registry_tab.refresh()
        self.verify_tab.refresh()

    def _backup(self):
        path, _ = QFileDialog.getSaveFileName(self, "Backup keystore",
                                              "ajj3_keystore_backup.json",
                                              "JSON (*.json)")
        if path:
            self.ks.backup(path)
            QMessageBox.information(self, "Backup",
                "Keystore backed up. Keep it somewhere safe and private — it "
                "contains every app's PRIVATE key.")

    def _restore(self):
        if QMessageBox.warning(self, "Restore",
                "Restoring REPLACES the current keystore. Continue?",
                QMessageBox.Yes | QMessageBox.No) != QMessageBox.Yes:
            return
        path, _ = QFileDialog.getOpenFileName(self, "Restore keystore", "",
                                              "JSON (*.json)")
        if not path:
            return
        try:
            self.ks.restore(path)
            self._refresh_all()
            QMessageBox.information(self, "Restore", "Keystore restored.")
        except Exception as e:
            QMessageBox.critical(self, "Restore", f"Could not restore:\n{e}")

    def _about(self):
        QMessageBox.about(self, "About",
            f"<b>{APP_NAME}</b> v{APP_VERSION}<br>by AJJ3<br><br>"
            "Offline license-key minting for the AJJ3 apps.<br>"
            "Pure-stdlib RSA, PySide6. Private keys never leave this tool.")


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setWindowIcon(_app_icon())
    app.setStyleSheet(STYLESHEET)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
