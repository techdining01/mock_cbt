"""
LLS-CBT Offline License Crypto
================================
Key format:  XXXX-XXXX-XXXX-XXXX  (16 alphanumeric chars + 3 dashes)

Encoding (all base32-uppercase, no padding):
    [0:4]   machine token  — first 4 chars of base32(machine_fingerprint[:3])
                             OR "AAAA" for any-machine keys
    [4:8]   expiry token   — base32 of 2-byte days-since-epoch (big-endian)
    [8:10]  credits token  — base32 of 1-byte credits value
    [10:16] hmac check     — first 6 chars of base32(HMAC-SHA256(secret, body))

The HMAC covers the first 10 chars so the check cannot be forged without
knowing _HMAC_SECRET, which is compiled into the app.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import struct
from datetime import datetime, date, timedelta
from typing import Any

# ---------------------------------------------------------------------------
# Secret — baked into the binary, never in a file
# Change this if you ever need to invalidate all existing keys.
# ---------------------------------------------------------------------------
_HMAC_SECRET = bytes.fromhex(
    "2ecec492be11eb4351a825865fce7845"
    "fdf72fa5152f90e4b732a998a9a1f2bf"
)

_EPOCH = date(2024, 1, 1)   # day-0 for the 2-byte expiry counter
_ANY_MACHINE = "AAAA"       # sentinel for unbound keys


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _b32(data: bytes) -> str:
    return base64.b32encode(data).decode().rstrip("=").upper()


def _b32dec(s: str) -> bytes:
    s = s.upper()
    pad = (8 - len(s) % 8) % 8
    return base64.b32decode(s + "=" * pad)


def _hmac_check(body10: str) -> str:
    """Return 6-char base32 HMAC tag over the first 10 key chars."""
    tag = hmac.new(_HMAC_SECRET, body10.encode(), hashlib.sha256).digest()
    return _b32(tag)[:6]


def _machine_token(machine_fingerprint: str | None) -> str:
    """4-char token derived from the machine fingerprint, or AAAA."""
    if not machine_fingerprint:
        return _ANY_MACHINE
    raw = bytes.fromhex(machine_fingerprint[:8])   # 4 bytes → 8 hex chars
    return _b32(raw)[:4]


def _expiry_token(expiry_date: date) -> str:
    """4-char token: days since _EPOCH as 2-byte big-endian → base32."""
    days = (expiry_date - _EPOCH).days
    days = max(0, min(days, 0xFFFF))
    return _b32(struct.pack(">H", days))[:4]


def _credits_token(credits: int) -> str:
    """2-char token: 1-byte credits value → base32."""
    return _b32(bytes([max(1, min(credits, 255))]))[:2]


def _decode_expiry_token(token: str) -> date:
    raw  = _b32dec(token.ljust(8, "A"))
    days = struct.unpack(">H", raw[:2])[0]
    return _EPOCH + timedelta(days=days)


def _decode_credits_token(token: str) -> int:
    raw = _b32dec(token.ljust(8, "A"))
    return raw[0] if raw else 1


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_key(
    machine_fingerprint: str | None,
    credits: int,
    expiry_date: date,
) -> str:
    """
    Generate a 16-char product key: XXXX-XXXX-XXXX-XXXX
    """
    m = _machine_token(machine_fingerprint)
    e = _expiry_token(expiry_date)
    c = _credits_token(credits)
    body = m + e + c                    # 10 chars
    h    = _hmac_check(body)            # 6 chars
    raw  = body + h                     # 16 chars
    return f"{raw[0:4]}-{raw[4:8]}-{raw[8:12]}-{raw[12:16]}"


def decode_key(product_key: str) -> dict[str, Any]:
    """
    Verify and decode a product key.
    Returns payload dict or raises ValueError.
    """
    raw = (
        product_key.strip()
        .replace("-", "")
        .replace(" ", "")
        .upper()
    )

    if len(raw) != 16:
        raise ValueError(f"Product key must be 16 characters (got {len(raw)}).")

    body   = raw[:10]
    h_recv = raw[10:16]
    h_calc = _hmac_check(body)

    if not hmac.compare_digest(h_recv, h_calc):
        raise ValueError("Product key is invalid or has been tampered with.")

    machine_token  = body[0:4]
    expiry_token   = body[4:8]
    credits_token  = body[8:10]

    expiry  = _decode_expiry_token(expiry_token)
    credits = _decode_credits_token(credits_token)
    machine = None if machine_token == _ANY_MACHINE else machine_token

    return {
        "machine_token" : machine_token,
        "machine"       : machine,       # None = any-machine key
        "expiry"        : expiry.isoformat(),
        "credits"       : credits,
    }


def validate_payload(
    payload: dict[str, Any],
    machine_fingerprint: str,
    credits_used: int = 0,
) -> dict[str, Any]:
    """
    Check expiry, credits, and machine binding after decode_key().
    """
    # --- Expiry ---
    try:
        expiry_dt = date.fromisoformat(payload["expiry"])
    except Exception:
        return {"valid": False, "message": "License expiry is malformed.", "remaining_credits": 0, "expiry": ""}

    if date.today() > expiry_dt:
        return {"valid": False, "message": "This license has expired.", "remaining_credits": 0, "expiry": payload["expiry"]}

    # --- Credits ---
    remaining = int(payload.get("credits", 0)) - credits_used
    if remaining <= 0:
        return {"valid": False, "message": "All activation credits for this key have been used.", "remaining_credits": 0, "expiry": payload["expiry"]}

    # --- Machine binding ---
    bound_token = payload.get("machine")   # None = any-machine
    if bound_token:
        current_token = _machine_token(machine_fingerprint)
        if current_token != bound_token:
            return {"valid": False, "message": "This product key is locked to a different machine.", "remaining_credits": 0, "expiry": payload["expiry"]}

    return {"valid": True, "message": "License is valid.", "remaining_credits": remaining, "expiry": payload["expiry"]}
