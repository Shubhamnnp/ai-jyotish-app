"""
At-Rest Symmetric Encryption for Sensitive Birth & Astrological Data (Phase 6, Task P6-T7).
Reference: docs/IMPLEMENTATION_PRD.md (Section 6.7, P6-T7).

Rules:
1. Encrypts sensitive personal data (names, cities, notes, contacts) at rest.
2. Uses authenticated symmetric encryption (Fernet AES-128-CBC + HMAC-SHA256).
3. Backwards-compatible: unencrypted values are handled cleanly and gracefully without crashing.
"""

import os
import base64
import hashlib
from typing import Dict, Any, List, Optional
from cryptography.fernet import Fernet, InvalidToken

DEFAULT_DEV_SECRET = "jyotish-shastriya-default-at-rest-secret-key-2026"
ENCRYPTION_PREFIX = "enc::v1::"

DEFAULT_SENSITIVE_FIELDS: List[str] = [
    "name", "birth_name", "city", "email", "phone", "mobile", "notes", "contact"
]


class DataPrivacyCrypto:
    """Provides at-rest encryption and decryption for sensitive client records."""

    def __init__(self, secret_key: Optional[str] = None):
        raw_key = secret_key or os.getenv("JYOTISH_ENCRYPTION_KEY", DEFAULT_DEV_SECRET)
        # Derive valid 32-byte URL-safe base64 Fernet key deterministically
        digest = hashlib.sha256(raw_key.encode("utf-8")).digest()
        self._fernet_key = base64.urlsafe_b64encode(digest)
        self._cipher = Fernet(self._fernet_key)

    def encrypt(self, plaintext: str) -> str:
        """Encrypts plaintext string and prefixes with enc::v1:: marker."""
        if not plaintext:
            return ""
        if str(plaintext).startswith(ENCRYPTION_PREFIX):
            return str(plaintext)  # Already encrypted
        token = self._cipher.encrypt(str(plaintext).encode("utf-8")).decode("utf-8")
        return f"{ENCRYPTION_PREFIX}{token}"

    def decrypt(self, ciphertext: str) -> str:
        """Decrypts an enc::v1:: string, or returns it unmodified if unencrypted."""
        if not ciphertext:
            return ""
        c_str = str(ciphertext)
        if not c_str.startswith(ENCRYPTION_PREFIX):
            return c_str  # Not encrypted / legacy plaintext

        token = c_str[len(ENCRYPTION_PREFIX):]
        try:
            return self._cipher.decrypt(token.encode("utf-8")).decode("utf-8")
        except InvalidToken:
            return c_str  # Decryption failure fallback (avoid fatal crashes)

    def encrypt_birth_data(
        self,
        birth_data: Dict[str, Any],
        fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Returns a copy of birth data dict with sensitive fields encrypted."""
        target_fields = fields or DEFAULT_SENSITIVE_FIELDS
        out = dict(birth_data)
        for f in target_fields:
            if f in out and isinstance(out[f], str):
                out[f] = self.encrypt(out[f])
        return out

    def decrypt_birth_data(
        self,
        birth_data: Dict[str, Any],
        fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Returns a copy of birth data dict with encrypted fields decrypted."""
        target_fields = fields or DEFAULT_SENSITIVE_FIELDS
        out = dict(birth_data)
        for f in target_fields:
            if f in out and isinstance(out[f], str):
                out[f] = self.decrypt(out[f])
        return out


default_crypto = DataPrivacyCrypto()

