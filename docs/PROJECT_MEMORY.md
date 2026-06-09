# Project Memory

## Decisions
- 2026-06-03 — Modular layout (chosen by user): `main.py` + `keycrypto.py` +
  `keystore.py` + `helpers.py` + `ui_theme.py` + `tabs/` (one file per tab), to
  keep each file small and easy to paste.
- 2026-06-03 — `keycrypto.py` used verbatim as supplied; not re-implemented.
- 2026-06-03 — Per-app keypair is the only scope; no app tag inside the key. A
  key minted for one app fails verification in another (confirmed by test).
- 2026-06-03 — Keystore is one JSON file at `~/.ajj3_license_manager/`,
  permission-locked on every save (POSIX 600 / Windows icacls, best-effort).
  Saves are atomic (temp file + os.replace).
- 2026-06-03 — Non-flat 3D look implemented as a single shared QSS in
  `ui_theme.py` (gradient panels, beveled buttons, sunken fields). New palette;
  no prior colors to preserve.
- 2026-06-03 — Build wired via `pyproject.toml [tool.nuitka_builder]` (not
  `build_config.toml`), matching the shared build.py schema (app/build/nuitka/
  icons tables). `requirements.txt` pins PySide6.
- 2026-06-03 — `include_qt_plugins` omitted on purpose. App is QtWidgets-only
  (no QML, no QtPrintSupport), so the pyside6 plugin default ("sensible") is
  enough. Avoided "all" (used in the other apps' configs) because build.py's own
  notes flag that "all" pulls in the QML tree and breaks Linux builds via
  patchelf. Set "sensible,printsupport" only if printing is added later.

## Known constraints
- stdlib crypto + PySide6 only; no third-party crypto.
- Private keys never leave this tool; never in repo or any build.
- Re-generating an app's keypair invalidates all previously issued keys for it.

## Open items
- (none) — full Nuitka compile to be run on a build host; config resolution
  confirmed via `build.py --audit` (exit 0, no issues).

## Changelog
- 2026-06-03 — Initial build: full PySide6 app (4 tabs), keystore, theme,
  helpers, keycrypto (verbatim), five-file doc set. Crypto round-trip,
  cross-app rejection, keystore persistence/perms/backup-restore all tested.
- 2026-06-03 — Added pyproject.toml [tool.nuitka_builder] + requirements.txt;
  validated against the shared build.py (--audit exit 0).
- 2026-06-03 — Registry: added Delete button + Keystore.delete_entry to remove
  an issued key from the local record (with confirmation; not a revocation).
- 2026-06-03 — Apps: added Delete app button + Keystore.delete_app, which removes
  the app, its keypair, and all its registry rows (strong warning; other apps
  unaffected). Documented in USER_GUIDE and HELP.
- 2026-06-03 — Stale-key indicator. helpers.entry_state classifies each registry
  row vs its app's current key: red = no longer verifies (keypair re-generated /
  app gone), amber = edited after minting (name/exp/tier ≠ baked-in). Registry
  rows are tinted with tooltips + a "⚠ re-mint" status note; Apps tab shows a
  per-app count. Re-issue now replaces the row in place (Keystore.reissue_entry)
  and clears the tint instead of appending a new row. Editing a name/notes or
  re-generating a keypair never auto-re-mints; renaming an app and editing notes
  remain harmless (not part of the signed key).
- 2026-06-03 — Apps: added "Re-issue all stale keys" button (enabled only when
  the selected app has stale keys) that re-mints every red/amber row for that app
  in place via reissue_entry, with a confirmation naming the count. Local records
  only; does not touch keys already delivered.
