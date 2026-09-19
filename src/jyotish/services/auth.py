"""
JyotishOS Enterprise Authentication & User Management Service.
Features:
1. PBKDF2-HMAC-SHA256 Cryptographic Password Hashing & Salt Verification
2. Persistent Registered User Storage (data/users.json)
3. Role-Based Access Control (Astrologer, Researcher, Client)
4. Secure Password Reset & OTP Flow
"""

import os
import json
import hashlib
import secrets
from typing import Dict, Any, Optional, Tuple


class AuthService:
    """Manages user authentication, registration, password encryption, and reset."""

    def __init__(self, storage_path: Optional[str] = None):
        if storage_path is None:
            curr_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.abspath(os.path.join(curr_dir, "..", "..", ".."))
            data_dir = os.path.join(project_root, "data")
            os.makedirs(data_dir, exist_ok=True)
            self.storage_path = os.path.join(data_dir, "users.json")
        else:
            self.storage_path = storage_path
            
        self._active_otps: Dict[str, str] = {}
        self._ensure_seed_users()

    def _hash_password(self, password: str, salt: Optional[str] = None) -> Tuple[str, str]:
        """Hash a password using PBKDF2-HMAC-SHA256 with 100,000 iterations and salt."""
        if salt is None:
            salt = secrets.token_hex(16)
        key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        )
        return salt, key.hex()

    def _verify_password(self, plain_password: str, salt: str, hashed_key: str) -> bool:
        """Verify plain password against stored salt and hashed key."""
        _, computed_key = self._hash_password(plain_password, salt)
        return secrets.compare_digest(computed_key, hashed_key)

    def _load_users(self) -> Dict[str, Any]:
        """Load all registered users from storage."""
        if not os.path.exists(self.storage_path):
            return {}
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_users(self, users: Dict[str, Any]) -> None:
        """Save users safely to storage."""
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=2, ensure_ascii=False)

    def _ensure_seed_users(self) -> None:
        """Seed default master accounts if storage is empty or missing."""
        users = self._load_users()
        seeds = [
            {
                "email": "shubham8jyotish@gmail.com",
                "password": "Bahraich@123",
                "name": "Shubham Tiwari",
                "role": "🔮 मुख्य ज्योतिषी (Chief Astrologer)"
            },
            {
                "email": "admin@jyotishos.com",
                "password": "Admin@2026",
                "name": "JyotishOS Admin",
                "role": "🔮 मुख्य ज्योतिषी (Chief Astrologer)"
            },
            {
                "email": "researcher@jyotishos.com",
                "password": "Research@2026",
                "name": "Vedic Researcher",
                "role": "🔬 वैदिक शोधकर्ता (Researcher)"
            }
        ]
        
        modified = False
        for s in seeds:
            email_lower = s["email"].strip().lower()
            if email_lower not in users:
                salt, pwd_hash = self._hash_password(s["password"])
                users[email_lower] = {
                    "email": s["email"],
                    "name": s["name"],
                    "role": s["role"],
                    "salt": salt,
                    "password_hash": pwd_hash,
                    "created_at": "2026-01-01T00:00:00"
                }
                modified = True
                
        if modified:
            self._save_users(users)

    def authenticate(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user against registered database with encrypted password comparison."""
        email_lower = email.strip().lower()
        users = self._load_users()
        user = users.get(email_lower)
        if not user:
            return None
        
        salt = user.get("salt", "")
        pwd_hash = user.get("password_hash", "")
        if self._verify_password(password, salt, pwd_hash):
            return {
                "email": user.get("email", email),
                "name": user.get("name", "User"),
                "role": user.get("role", "🔮 मुख्य ज्योतिषी (Chief Astrologer)")
            }
        return None

    def register(self, email: str, password: str, name: str, role: str) -> Tuple[bool, str]:
        """Register a new user with encrypted password."""
        email_lower = email.strip().lower()
        if not email_lower or "@" not in email_lower:
            return False, "कृपया मान्य ईमेल पता दर्ज करें।"
        if len(password) < 6:
            return False, "पासवर्ड कम से कम 6 अक्षरों का होना चाहिए।"
        if not name.strip():
            return False, "कृपया अपना नाम दर्ज करें।"

        users = self._load_users()
        if email_lower in users:
            return False, "यह ईमेल आईडी पहले से पंजीकृत है। कृपया लॉगिन करें या पासवर्ड रीसेट करें।"

        salt, pwd_hash = self._hash_password(password)
        users[email_lower] = {
            "email": email.strip(),
            "name": name.strip(),
            "role": role,
            "salt": salt,
            "password_hash": pwd_hash
        }
        self._save_users(users)
        return True, "पंजीकरण सफल! अब आप लॉगिन कर सकते हैं।"

    def request_reset_code(self, email: str) -> Tuple[bool, str, Optional[str]]:
        """Generate a 6-digit OTP for password reset."""
        email_lower = email.strip().lower()
        users = self._load_users()
        if email_lower not in users:
            return False, "यह ईमेल आईडी सिस्टम में पंजीकृत नहीं है।", None

        # Generate 6-digit OTP
        otp = f"{secrets.randbelow(900000) + 100000}"
        self._active_otps[email_lower] = otp
        return True, f"सत्यापन कोड (OTP) उत्पन्न हुआ: {otp}", otp

    def reset_password(self, email: str, otp_code: str, new_password: str) -> Tuple[bool, str]:
        """Verify OTP and update encrypted password."""
        email_lower = email.strip().lower()
        if len(new_password) < 6:
            return False, "नया पासवर्ड कम से कम 6 अक्षरों का होना चाहिए।"

        stored_otp = self._active_otps.get(email_lower)
        if not stored_otp or stored_otp.strip() != otp_code.strip():
            return False, "अमान्य या समाप्त सत्यापन कोड (Invalid OTP)।"

        users = self._load_users()
        if email_lower not in users:
            return False, "उपयोगकर्ता नहीं मिला।"

        salt, pwd_hash = self._hash_password(new_password)
        users[email_lower]["salt"] = salt
        users[email_lower]["password_hash"] = pwd_hash
        self._save_users(users)
        
        # Clear OTP
        self._active_otps.pop(email_lower, None)
        return True, "पासवर्ड सफलतापूर्वक रीसेट हो गया! अब नए पासवर्ड से लॉगिन करें।"


default_auth_service = AuthService()

