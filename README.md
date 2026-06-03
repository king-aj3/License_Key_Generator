# AJJ3 License Manager

A PySide6 desktop tool that mints offline license keys for the AJJ3 apps
(My_LLM, WealthBuilder, Thrift Reseller, …). It holds every app's RSA private
key and signs keys locally. Each app embeds only its own public key and verifies
— a key minted for one app will not verify in another, because the per-app
keypair *is* the scope. Crypto is pure standard library (`keycrypto.py`, RSA via
`pow()`); the only dependency is PySide6.

## Install & run
Requires Python 3.10+ and PySide6.

    pip install PySide6
    python main.py

The keystore is created on first run at `~/.ajj3_license_manager/keystore.json`
and is permission-locked to your user (POSIX chmod 600 / Windows icacls). It is
never placed in the repo or a build.

## Project layout
- `main.py` — window, tabs, Keystore menu (Backup/Restore/About)
- `keycrypto.py` — pure-stdlib RSA sign/verify (shared verbatim with the apps)
- `keystore.py` — apps + issued-key registry, locked persistence, backup/restore
- `helpers.py` — fingerprint, public-key constant block
- `ui_theme.py` — single non-flat 3D stylesheet
- `tabs/` — `apps_tab`, `mint_tab`, `registry_tab`, `verify_tab`
- `docs/` — USER_GUIDE, PROJECT_MEMORY

## Build
Intended to build with the shared `Build_Scripts/build.py` driven by
`pyproject.toml [tool.nuitka_builder]`. The pyproject is added once an example
of your build schema is supplied (see PROJECT_MEMORY → Open items).

## Workflow
Apps tab → add an app → Generate keypair (once) → copy its public-key block into
that app project. Mint tab → produce keys. Registry tab → track them. Verify tab
→ confirm a key against an app's public key.
