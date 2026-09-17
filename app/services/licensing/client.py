"""
Offline LicenseClient for LLS-CBT.

Activation flow:
  1. User pastes product key.
  2. decode_key()  — verifies RSA-PSS signature with embedded public key.
  3. validate_payload() — checks expiry, credits, machine binding.
  4. Deduct one credit and save license file to user home directory.
  5. On every subsequent launch, validate_license() re-checks the saved file
     (signature + expiry + machine) — no internet required.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from app.services.licensing.crypto import decode_key, validate_payload
from app.services.licensing.machine_fingerprint import MachineFingerprint


_LICENSE_FILE = Path.home() / ".lls_cbt_license.json"


class LicenseClient:

    def __init__(self, license_server_url: str = ""):
        # license_server_url kept for API compatibility but unused
        self.machine_fingerprint = MachineFingerprint.get_machine_id()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def activate_license(self, product_key: str, user_email: str = "", user_name: str = "") -> dict[str, Any]:
        """
        Verify the product key offline and save the license locally.
        Consumes one credit.
        """
        product_key = self._normalise_key(product_key)

        # 1. Verify signature
        try:
            payload = decode_key(product_key)
        except ValueError as exc:
            return {"success": False, "message": str(exc)}

        # 2. How many credits already used on this machine?
        credits_used = self._credits_used_locally(product_key)

        # 3. Validate payload (expiry, credits, machine binding)
        result = validate_payload(payload, self.machine_fingerprint, credits_used)
        if not result["valid"]:
            return {"success": False, "message": result["message"]}

        # 4. Consume one credit and persist
        self._save_license(
            product_key=product_key,
            payload=payload,
            credits_used=credits_used + 1,
            user_email=user_email,
            user_name=user_name,
        )

        remaining = result["remaining_credits"] - 1  # we just used one
        return {
            "success": True,
            "message": "License activated successfully.",
            "remaining_credits": max(0, remaining),
            "expiry_date": result["expiry"],
        }

    def validate_license(self) -> dict[str, Any]:
        """
        Validate the saved license on every app launch — fully offline.
        """
        saved = self._load_license()
        if not saved:
            return {"success": False, "message": "No license found. Please activate your product."}

        # Re-verify the key signature (tamper detection)
        try:
            payload = decode_key(saved["product_key"])
        except ValueError as exc:
            return {"success": False, "message": f"License file is invalid: {exc}"}

        # Validate payload with the stored credits_used count
        result = validate_payload(
            payload,
            self.machine_fingerprint,
            saved.get("credits_used", 1),
        )
        if not result["valid"]:
            return {"success": False, "message": result["message"]}

        return {
            "success": True,
            "message": "License is valid.",
            "remaining_credits": result["remaining_credits"],
            "expiry_date": result["expiry"],
        }

    def is_licensed(self) -> bool:
        return self.validate_license().get("success", False)

    def get_license_info(self) -> dict[str, Any] | None:
        return self._load_license()

    def deactivate_license(self) -> dict[str, Any]:
        if _LICENSE_FILE.exists():
            _LICENSE_FILE.unlink()
        return {"success": True, "message": "License removed from this machine."}

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _normalise_key(key: str) -> str:
        return key.strip().replace("-", "").replace(" ", "").replace("\r", "").replace("\n", "").upper()

    def _credits_used_locally(self, normalised_key: str) -> int:
        """Return credits already consumed if the same key is saved on this machine."""
        saved = self._load_license()
        if not saved:
            return 0
        saved_key = self._normalise_key(saved.get("product_key", ""))
        saved_machine = saved.get("machine_fingerprint", "")
        # Only reuse credits_used if same key AND same machine
        if saved_key == normalised_key and saved_machine == self.machine_fingerprint:
            return saved.get("credits_used", 1)
        return 0

    def _save_license(
        self,
        product_key: str,
        payload: dict,
        credits_used: int,
        user_email: str,
        user_name: str,
    ) -> None:
        data = {
            "product_key"        : product_key,
            "payload"            : payload,
            "credits_used"       : credits_used,
            "machine_fingerprint": self.machine_fingerprint,
            "user_email"         : user_email,
            "user_name"          : user_name,
            "activated_at"       : datetime.utcnow().isoformat(timespec="seconds"),
            # legacy fields kept so the dialog can display them
            "license_data"       : payload,
            "expiry_date"        : payload.get("expiry", ""),
            "last_validated"     : datetime.utcnow().isoformat(timespec="seconds"),
        }
        _LICENSE_FILE.write_text(json.dumps(data, indent=2))

    @staticmethod
    def _load_license() -> dict[str, Any] | None:
        if not _LICENSE_FILE.exists():
            return None
        try:
            return json.loads(_LICENSE_FILE.read_text())
        except Exception:
            return None
