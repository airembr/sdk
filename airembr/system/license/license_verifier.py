import json
import base64
from datetime import datetime
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import InvalidSignature


class LicenseVerifier:
    """
    Verifies RSA-signed licenses using only the public key.

    Usage:
        # From a PEM string
        verifier = LicenseVerifier(public_key_pem="-----BEGIN PUBLIC KEY-----...")

        # From a file
        verifier = LicenseVerifier(public_key_path="public.pem")

        result = verifier.verify("eyJwYXlsb2FkI...")
        if result.valid:
            print(f"Licensed to: {result.owner}, expires: {result.valid_until}")
        else:
            print(f"Invalid: {result.error}")
    """

    class Result:
        """Structured result returned by verify()."""

        def __init__(self, valid: bool, owner: str = None,
                     valid_until: datetime = None, issued_at: datetime = None,
                     error: str = None):
            self.valid       = valid
            self.owner       = owner
            self.valid_until = valid_until
            self.issued_at   = issued_at
            self.error       = error

        def __repr__(self):
            if self.valid:
                days_left = (self.valid_until - datetime.utcnow()).days
                return (
                    f"<LicenseResult VALID | owner='{self.owner}' "
                    f"valid_until={self.valid_until.strftime('%Y-%m-%d')} "
                    f"({days_left}d left)>"
                )
            return f"<LicenseResult INVALID | error='{self.error}'>"

        def __bool__(self):
            return self.valid

    # ── Construction ──────────────────────────────────────────────────────────

    def __init__(self, public_key_pem: str = None, public_key_path: str = None):
        """
        Provide exactly one of:
          public_key_pem  — PEM string (e.g. embedded in your application)
          public_key_path — path to a .pem file on disk
        """
        if public_key_pem and public_key_path:
            raise ValueError("Provide public_key_pem OR public_key_path, not both.")
        if not public_key_pem and not public_key_path:
            raise ValueError("Provide either public_key_pem or public_key_path.")

        if public_key_pem:
            self._public_key = load_pem_public_key(public_key_pem.encode())
        else:
            with open(public_key_path, "rb") as f:
                self._public_key = load_pem_public_key(f.read())

    # ── Public API ────────────────────────────────────────────────────────────

    def verify(self, license_str: str) -> "LicenseVerifier.Result":
        """
        Verify a license string produced by LicenseIssuer.

        Checks:
          1. The license string is well-formed and not corrupted.
          2. The RSA signature is authentic (not forged or tampered).
          3. The license has not expired.

        Returns a LicenseVerifier.Result — truthy on success, falsy on failure.
        """
        payload_bytes, signature = self._decode(license_str)
        if payload_bytes is None:
            return self.Result(valid=False, error="Malformed license — could not decode")

        if not self._verify_signature(payload_bytes, signature):
            return self.Result(valid=False, error="Invalid signature — license may be forged or tampered")

        return self._check_payload(payload_bytes)

    # ── Private helpers ───────────────────────────────────────────────────────

    def _decode(self, license_str: str):
        """Decode the base64 license string into (payload_bytes, signature)."""
        try:
            bundle       = json.loads(base64.b64decode(license_str).decode())
            payload_bytes = base64.b64decode(bundle["payload"])
            signature     = base64.b64decode(bundle["signature"])
            return payload_bytes, signature
        except Exception:
            return None, None

    def _verify_signature(self, payload_bytes: bytes, signature: bytes) -> bool:
        """Return True if the RSA signature is valid for the payload."""
        try:
            self._public_key.verify(signature, payload_bytes, padding.PKCS1v15(), hashes.SHA256())
            return True
        except InvalidSignature:
            return False

    def _check_payload(self, payload_bytes: bytes) -> "LicenseVerifier.Result":
        """Parse the payload and check expiry."""
        try:
            payload = json.loads(payload_bytes.decode())
        except Exception:
            return self.Result(valid=False, error="Malformed payload — could not parse JSON")

        try:
            valid_until = datetime.fromisoformat(payload["valid_until"])
            issued_at   = datetime.fromisoformat(payload["issued_at"])
            owner       = payload["owner"]
        except KeyError as e:
            return self.Result(valid=False, error=f"Missing field in payload: {e}")

        if datetime.utcnow() > valid_until:
            return self.Result(
                valid=False,
                error=f"License expired on {valid_until.strftime('%Y-%m-%d')}",
                owner=owner,
                valid_until=valid_until,
                issued_at=issued_at,
            )

        return self.Result(
            valid=True,
            owner=owner,
            valid_until=valid_until,
            issued_at=issued_at,
        )