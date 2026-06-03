#!/usr/bin/env python3
"""helpers.py -- tiny shared utilities used by more than one tab."""
from __future__ import annotations
import hashlib


def fingerprint(keypair_obj: dict | None) -> str:
    """Short, stable id for a key so you can confirm which key an app is on.
    Derived from the public modulus n only (safe to display)."""
    if not keypair_obj:
        return "—"
    digest = hashlib.sha256(keypair_obj["n"].encode()).hexdigest()[:16].upper()
    return ":".join(digest[i:i + 4] for i in range(0, 16, 4))


def pubkey_block(keypair_obj: dict) -> str:
    """Ready-to-paste public-key constant block for embedding in an app."""
    return (f'_PUBKEY_N = "{keypair_obj["n"]}"\n'
            f'_PUBKEY_E = {keypair_obj["e"]}')
