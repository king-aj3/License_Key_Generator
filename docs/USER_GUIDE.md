# User Guide

## 1. Add an app and generate its keypair
Open the Apps tab. Type a short id (e.g. `MLLM`) and a display name, then click
Add. Select the app and click Generate keypair. This is a one-time step per app
— the private key stays in this tool forever.

## 2. Embed the public key in your app
With the app selected, the public-key block is shown on the right:

    _PUBKEY_N = "…"
    _PUBKEY_E = 65537

Click Copy public-key block and paste it into that app's project (in Claude Code
or your editor). The app uses it with `keycrypto.verify_key` to check keys. Note
the fingerprint so you can confirm later which key the app is on.

## 3. Mint a license key
Open the Mint tab. Pick the app, choose a tier (AJJ3 = owner, FRIEND, BETA),
enter the licensee name, and set expiry — leave "Never expires" checked or pick a
date. Click Mint key. The key appears for copying and is recorded automatically
in the registry.

## 4. Track issued keys
Open the Registry tab to see every key across all apps. Filter by app, tier, or
name. Select a row to copy the key, edit the licensee name or notes, toggle a
revoked flag (tracking only), Re-issue, or Delete it (removes it from the
registry only — it does not disable a key already in use).

Rows are tinted when a key no longer reflects current reality, so you can see at
a glance what still needs re-minting:
- Red — the key no longer verifies against the app's current public key (you
  re-generated that app's keypair, for example). It is now invalid.
- Amber — the key still verifies, but the row was edited after minting (the
  licensee name no longer matches what is baked into the key).
Re-issue re-mints the key in place from the row's current details and clears the
tint (it replaces that row rather than adding a new one, and copies the fresh key
to the clipboard). The Apps tab shows a per-app count of keys needing re-mint and
a "Re-issue all stale keys" button that re-mints every red/amber key for the
selected app in one pass (handy after re-generating a keypair). Either way, only
your local records change — keys already delivered to users aren't touched, and
any that became invalid must be re-sent.

## 5. Delete an app
On the Apps tab, select the app and click Delete app. This permanently destroys
its keypair and removes all of its issued-key records. Use with care: any build
of that app already carrying the matching public key will then accept no key you
can mint here. (Deleting an app does not affect any other app.)

## 6. Verify a key
Open the Verify tab. Pick the app, paste a key, click Verify. A valid key shows
its tier, name, and expiry; a key minted for a different app shows INVALID.

## 7. Back up the keystore
Use Keystore → Backup regularly and store the file somewhere safe and private —
it contains every app's private key. Keystore → Restore replaces the current
keystore from a backup.
