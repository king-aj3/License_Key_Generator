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
revoked flag (tracking only), or re-issue a fresh key with the same details.

## 5. Verify a key
Open the Verify tab. Pick the app, paste a key, click Verify. A valid key shows
its tier, name, and expiry; a key minted for a different app shows INVALID.

## 6. Back up the keystore
Use Keystore → Backup regularly and store the file somewhere safe and private —
it contains every app's private key. Keystore → Restore replaces the current
keystore from a backup.
