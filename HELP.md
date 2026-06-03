# Help (symptom → fix)

**"No module named PySide6"** → `pip install PySide6`.

**Mint button warns "This app has no keypair yet"** → Go to the Apps tab, select
the app, and click Generate keypair (one time per app).

**A key won't verify in the app, but verifies here** → Confirm the app embeds
this app's public key. Compare the fingerprint shown in the Apps tab against the
one your app reports. A fingerprint mismatch means the app is on a different (or
old) key.

**I re-generated a keypair and old keys stopped working** → Expected.
Re-generating replaces the key; every previously issued key for that app stops
verifying and you must re-embed the new public-key block. Restore from a backup
if this was a mistake.

**"Revoked" key still works in the app** → Expected. Offline keys cannot be
cryptographically revoked; the status is a tracking flag only.

**Keystore file permissions didn't lock (Windows)** → icacls is best-effort. If
it failed, set the file private manually; the app still functions.

**Lost the keystore** → Restore from a backup (Keystore → Restore). Without a
backup the keys are unrecoverable and every app must be re-keyed. Back up often
(Keystore → Backup).

**A Registry row is red** → That key no longer verifies against the app's current
public key — usually because you re-generated that app's keypair. Select the row
and click Re-issue (then re-send/re-embed the new key).

**A Registry row is amber** → You edited that row (e.g. the licensee name) after
the key was minted, so the key still carries the old details. Click Re-issue to
re-mint it with the current details.

**Editing a name didn't change the key** → Correct. Editing the row updates your
record only; the signed key is unchanged until you Re-issue. The amber tint flags
exactly this.

**Where is my data?** → `~/.ajj3_license_manager/keystore.json`.

**How do I remove a key I issued?** → Registry tab, select the row, click Delete.
This clears it from your local record only; it can't disable a key already in
use (offline keys aren't revocable).

**How do I remove an app?** → Apps tab, select it, click Delete app. This destroys
its keypair and deletes its issued-key records permanently. Back up first
(Keystore → Backup) if you might want it later.
