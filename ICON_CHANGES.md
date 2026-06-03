# Icon wiring — changes in this zip

Two full files (drop into the project root, overwriting):
- `main.py`        — adds `_app_icon()` (win→ico, mac→icns, linux→png; PNG fallback) and `app.setWindowIcon(...)`
- `pyproject.toml` — `[tool.nuitka_builder.icons]` per OS + the three icons bundled via `data_files`

Prereq: icons already in `assets/` (`icon.ico`, `icon.icns`, `icon-256.png`).

## Paste-in doc edits (not shipped as files, so they don't clobber yours)

Append to `docs/PROJECT_MEMORY.md` → Changelog:
```
- 2026-06-03 — Added per-OS app icon in assets/ (icon.ico/.icns/-256.png + .svg source). main.py sets the window icon via _app_icon() (win→ico, mac→icns, linux→png, PNG fallback); pyproject wires [tool.nuitka_builder.icons] and bundles the three icons via data_files.
```

Add to `README.md` → Project layout list:
```
- `assets/` — app icons (icon.ico, icon.icns, icon-256/512.png, icon.svg)
```

Linux desktop integration: point your `.desktop` `Icon=` line at `assets/icon-256.png`.

```
Commit: feat: wire per-OS app icon (assets/) into runtime + Nuitka build
```
