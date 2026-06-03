#!/usr/bin/env python3
"""keycrypto.py -- pure-stdlib RSA signing/verification for offline license keys.
Identical file in the License Manager and every app it serves. Each app has its
OWN keypair: the PUBLIC key is compiled into that app (verify-only); the PRIVATE
keys live only here and never ship. Key = "AJK1.<payload_b64url>.<sig_b64url>";
payload = "<tier>|<name>|<exp>|<nonce>"  (tier AJJ3|ASAWA|FRIEND|BETA; exp "0"=never).
"""
from __future__ import annotations
import base64, hashlib, secrets

KEY_BITS = 1024
PUBLIC_EXPONENT = 65537
KEY_PREFIX = "AJK1"
PAYLOAD_SEP = "|"
TIERS = ("AJJ3", "ASAWA", "FRIEND", "BETA")

def _b64u(b): return base64.urlsafe_b64encode(b).decode().rstrip("=")
def _b64u_dec(s): return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))

def _is_probable_prime(n, rounds=40):
    if n < 2: return False
    for p in (2,3,5,7,11,13,17,19,23,29,31,37):
        if n % p == 0: return n == p
    d, r = n - 1, 0
    while d % 2 == 0: d //= 2; r += 1
    for _ in range(rounds):
        a = secrets.randbelow(n - 3) + 2
        x = pow(a, d, n)
        if x in (1, n - 1): continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1: break
        else: return False
    return True

def _gen_prime(bits):
    while True:
        c = secrets.randbits(bits) | (1 << (bits - 1)) | 1
        if _is_probable_prime(c): return c

def generate_keypair(bits=KEY_BITS):
    e = PUBLIC_EXPONENT
    while True:
        p = _gen_prime(bits // 2); q = _gen_prime(bits - bits // 2)
        if p == q: continue
        phi = (p - 1) * (q - 1)
        if phi % e == 0: continue
        return {"n": p * q, "e": e, "d": pow(e, -1, phi)}

def _digest_int(b): return int.from_bytes(hashlib.sha256(b).digest(), "big")

def sign_payload(payload, priv):
    n, d = priv["n"], priv["d"]
    sig = pow(_digest_int(payload.encode()) % n, d, n)
    return f"{KEY_PREFIX}.{_b64u(payload.encode())}.{_b64u(sig.to_bytes((n.bit_length()+7)//8,'big'))}"

def verify_key(key, pub):
    try:
        parts = key.strip().split(".")
        if len(parts) != 3 or parts[0] != KEY_PREFIX: return None
        payload = _b64u_dec(parts[1]); sig = int.from_bytes(_b64u_dec(parts[2]), "big")
        return payload.decode() if pow(sig, pub["e"], pub["n"]) == _digest_int(payload) % pub["n"] else None
    except Exception: return None

def make_payload(tier, name, exp="0", nonce=""):
    name = name.replace(PAYLOAD_SEP, "/").strip()
    return PAYLOAD_SEP.join([tier, name, exp or "0", nonce or secrets.token_hex(3)])

def parse_payload(payload):
    b = payload.split(PAYLOAD_SEP)
    return {} if len(b) < 4 else {"tier": b[0], "name": b[1], "exp": b[2], "nonce": b[3]}

def pub_to_obj(pub): return {"n": format(pub["n"], "x"), "e": pub["e"]}
def priv_to_obj(priv): return {"n": format(priv["n"], "x"), "e": priv["e"], "d": format(priv["d"], "x")}
def obj_to_key(o):
    out = {"e": int(o["e"]), "n": int(o["n"], 16)}
    if o.get("d"): out["d"] = int(o["d"], 16)
    return out
