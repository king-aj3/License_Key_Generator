#!/usr/bin/env python3
"""ui_theme.py -- one shared NON-FLAT, 3D stylesheet for the whole app.

Every window, tab, dialog and message box uses this so the look stays
consistent: raised beveled buttons, sunken inset fields, gradient panels.
Apply once on the QApplication: app.setStyleSheet(STYLESHEET).
"""
from __future__ import annotations

# Palette (single source of truth — change here to restyle everything).
BG      = "#2b313b"   # window base
PANEL   = "#353c47"   # raised panels / group boxes
FIELD   = "#222831"   # sunken inputs
TEXT    = "#e6e9ef"
ACCENT  = "#4a90d9"
BORDER_LIGHT = "#4c5563"
BORDER_DARK  = "#1c2128"

STYLESHEET = f"""
* {{
    color: {TEXT};
    font-size: 13px;
}}
QWidget {{
    background: {BG};
}}

/* ---- raised panels & group boxes (3D) ---- */
QGroupBox {{
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 {PANEL}, stop:1 {BG});
    border-top: 1px solid {BORDER_LIGHT};
    border-left: 1px solid {BORDER_LIGHT};
    border-right: 1px solid {BORDER_DARK};
    border-bottom: 1px solid {BORDER_DARK};
    border-radius: 6px;
    margin-top: 14px;
    padding: 10px;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 4px;
    color: {ACCENT};
    font-weight: bold;
}}

/* ---- beveled raised buttons (3D) ---- */
QPushButton {{
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 {BORDER_LIGHT}, stop:1 {PANEL});
    border-top: 1px solid {BORDER_LIGHT};
    border-left: 1px solid {BORDER_LIGHT};
    border-right: 1px solid {BORDER_DARK};
    border-bottom: 2px solid {BORDER_DARK};
    border-radius: 5px;
    padding: 6px 14px;
}}
QPushButton:hover {{ border-bottom: 2px solid {ACCENT}; }}
QPushButton:pressed {{
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 {PANEL}, stop:1 {BORDER_LIGHT});
    border-top: 2px solid {BORDER_DARK};
    border-bottom: 1px solid {BORDER_LIGHT};
    padding-top: 7px;
}}
QPushButton:disabled {{ color: #7d828c; border-bottom: 1px solid {BORDER_DARK}; }}

/* ---- sunken inset inputs (3D) ---- */
QLineEdit, QPlainTextEdit, QTextEdit, QDateEdit, QComboBox, QSpinBox {{
    background: {FIELD};
    border-top: 2px solid {BORDER_DARK};
    border-left: 2px solid {BORDER_DARK};
    border-right: 1px solid {BORDER_LIGHT};
    border-bottom: 1px solid {BORDER_LIGHT};
    border-radius: 4px;
    padding: 4px 6px;
    selection-background-color: {ACCENT};
}}
QComboBox::drop-down {{ border: none; width: 18px; }}

/* ---- tabs (raised) ---- */
QTabWidget::pane {{
    border: 1px solid {BORDER_DARK};
    border-radius: 6px;
    top: -1px;
}}
QTabBar::tab {{
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 {PANEL}, stop:1 {BG});
    border: 1px solid {BORDER_DARK};
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 7px 16px;
    margin-right: 2px;
}}
QTabBar::tab:selected {{
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 {ACCENT}, stop:1 {PANEL});
    border-top: 2px solid {ACCENT};
}}

/* ---- tables (sunken) ---- */
QTableWidget, QTableView {{
    background: {FIELD};
    border-top: 2px solid {BORDER_DARK};
    border-left: 2px solid {BORDER_DARK};
    border-right: 1px solid {BORDER_LIGHT};
    border-bottom: 1px solid {BORDER_LIGHT};
    border-radius: 4px;
    gridline-color: {BORDER_DARK};
}}
QHeaderView::section {{
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 {BORDER_LIGHT}, stop:1 {PANEL});
    border: 1px solid {BORDER_DARK};
    padding: 4px;
    font-weight: bold;
}}
QTableWidget::item:selected {{ background: {ACCENT}; }}
"""
