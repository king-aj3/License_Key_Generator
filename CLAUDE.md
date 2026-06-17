# AJJ3 License Manager (License_Key_Generator)
**What it is.** A PySide6 desktop tool that is the single offline authority for minting RSA-signed license keys for the AJJ3 apps (AJJ³ Brain, WealthBuilder, Thrift Reseller, …). It holds every app's private key and signs locally; each app embeds only its own public key and verifies, so a key minted for one app won't verify in another (the per-app keypair *is* the scope).
**Status.** Commercial / active — v1.0.0, keys feed paid AJJ3 apps. Internal tool: nothing here ships to customers.

## Stack & layout
- Python 3.10+, PySide6 (QtWidgets only). Pure-stdlib crypto — no third-party crypto lib.
- Entry point: `main.py` (QMainWindow + 4-tab QTabWidget + Keystore menu).
- `keycrypto.py` — pure-stdlib RSA sign/verify, shared verbatim with the apps; key format `AJK1.<payload>.<sig>`.
- `keystore.py` — apps + issued-key registry; locked JSON persistence, backup/restore.
- `helpers.py` — fingerprint + public-key constant block. `ui_theme.py` — single 3D QSS stylesheet.
- `tabs/` — `apps_tab`, `mint_tab`, `registry_tab`, `verify_tab` (one file per tab).
- Build/dist: Nuitka via shared `Build_Scripts/build.py` (reads `[tool.nuitka_builder]` in `pyproject.toml`); onefile exe in `dist/`. `requirements.txt` pins PySide6.

## How to run / build / test
```
pip install PySide6
python main.py
# build (onefile exe) — needs the shared Build_Scripts repo:
python /path/to/Build_Scripts/build.py .            # default onefile
python /path/to/Build_Scripts/build.py . --audit    # validate config (exit 0 = ok)
python /path/to/Build_Scripts/build.py . --standalone
# TODO: no automated test suite found — crypto round-trip/cross-app rejection tested manually only
```

## Conventions (match existing code)
- Modular by design: small files, one tab per module, easy to paste.
- `keycrypto.py` is used verbatim and is identical in every app — do not diverge it.
- Keystore saves are atomic (temp + `os.replace`) and permission-locked (POSIX 600 / Windows icacls) every save.

## Fragile / do-NOT-touch
- Private keys live ONLY in `~/.ajj3_license_manager/keystore.json` — never commit, never put in a build, never in the repo.
- Re-generating an app's keypair invalidates ALL previously issued keys for that app.
- Offline keys cannot be cryptographically revoked — "revoked" is only a registry tracking flag.
- `keycrypto.py` must stay byte-identical to the copy embedded in each consuming app, or verification breaks.
- `build/` C files are Nuitka output, not source — don't edit.

## How I want you to work on this project
- Walk me through consequences before any destructive or behavior-changing edit: what the code does today, what changes, your confidence, and what could break — then wait for my yes/no. Batch only clearly-safe sweeps.
- Edit files directly on disk (I reload in PyCharm); don't hand me paste-in patches unless I ask.
- Prefer completing a half-built feature over deleting it, when that's a real option.
- After each change, run the smoke/compile check and report a clean state before moving on.
- I'm cautious about breaking working/production behavior — when in doubt, ask.

## Git
- Branch: master; remote: origin → https://github.com/king-aj3/License_Key_Generator.git
- Commit/push only when I ask.

## Pointers
- `PROJECT_MEMORY.md` (+ `docs/PROJECT_MEMORY.md`) — decision log. `ABOUT.md`, `HELP.md`, `USER_GUIDE.md`, `README.md` — user-facing docs.
- Related: consuming apps AJJ³ Brain, WealthBuilder, Thrift Reseller (each embeds its own public key). Build via shared `Build_Scripts/build.py`.
