# About

AJJ3 License Manager is the single, offline authority for minting license keys
for the AJJ3 family of apps. It exists so that key signing — and therefore every
private key — lives in exactly one place, never in a shipped app and never in a
repository.

## Goal
Make it easy to manage one RSA keypair per app, mint signed keys for each, keep
a registry of what was issued, and confirm keys — all offline, with no
third-party crypto.

## Scope
- In scope: per-app keypair generation, public-key export for embedding, key
  minting, an issued-key registry, verification, and keystore backup/restore.
- Out of scope: networked activation, true cryptographic revocation (offline
  keys can't be revoked; "revoked" is a tracking flag), and any customer-facing
  distribution. Nothing here ships to customers.

Author/company: AJJ3.
