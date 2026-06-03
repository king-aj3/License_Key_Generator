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
- 2026-06-03 — "Revoked" is a tracking flag only; documented in UI and HELP that
  offline keys can't be cryptographically revoked.

## Known constraints
- stdlib crypto + PySide6 only; no third-party crypto.
- Private keys never leave this tool; never in repo or any build.
- Re-generating an app's keypair invalidates all previously issued keys for it.

## Open items
- pyproject.toml `[tool.nuitka_builder]` not yet written — waiting on an example
  of the user's build schema to match it exactly, then wire to the shared
  `Build_Scripts/build.py`.

## Changelog
- 2026-06-03 — Initial build: full PySide6 app (4 tabs), keystore, theme,
  helpers, keycrypto (verbatim), five-file doc set. Crypto round-trip,
  cross-app rejection, keystore persistence/perms/backup-restore all tested.
