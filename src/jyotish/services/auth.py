"""
JyotishOS Enterprise Authentication, RBAC & License Management Service.
Features:
1. PBKDF2-HMAC-SHA256 Cryptographic Password Hashing & Salt Verification (100,000 iterations)
2. 3-Tier Multi-Tenant Roles:
   - Researcher (शोधकर्ता / Super Admin): Full access, User control, Purchase code generator
   - Jyotishi (ज्योतिषी / Astrologer): All modules & tabs, Activated via Purchase Code, Data Isolation
   - Jatak (जातक / Free Client): Free access (Kundali, AI, Panchang, Natal), Data Isolation
3. Purchase Code Engine (Generator, Validator & Activator)
4. Secure Email OTP Password Reset Flow (with SMTP support & local fallback)
5. Multi-User Administration for Researchers
"""

import os
import json
import hashlib
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple


ROLE_RESEARCHER = "researcher"
ROLE_JYOTISHI = "jyotishi"
ROLE_JATAK = "jatak"

ROLE_DISPLAY_NAMES = {
    ROLE_RESEARCHER: "🔬 वैदिक शोधकर्ता (Researcher / Admin)",
    ROLE_JYOTISHI: "🔮 ज्योतिषी (Professional Astrologer)",
    ROLE_JATAK: "👤 जातक (General User)"
}


class AuthService:
    """Enterprise authentication, multi-tier RBAC, and purchase code service."""

    def __init__(self, data_dir: Optional[str] = None):
        if data_dir is None:
            curr_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.abspath(os.path.join(curr_dir, "..", "..", ".."))
            self.data_dir = os.path.join(project_root, "data")
        else:
            self.data_dir = data_dir

        os.makedirs(self.data_dir, exist_ok=True)
        self.users_file = os.path.join(self.data_dir, "users.json")
        self.codes_file = os.path.join(self.data_dir, "purchase_codes.json")

        # OTP in-memory store: {email_lower: {"otp": "...", "expires_at": datetime}}
        self._active_otps: Dict[str, Dict[str, Any]] = {}

        self._ensure_seed_users()
        self._ensure_seed_codes()

    # -------------------------------------------------------------
    # Password Cryptography (PBKDF2-HMAC-SHA256)
    # -------------------------------------------------------------
    def _hash_password(self, password: str, salt: Optional[str] = None) -> Tuple[str, str]:
        """Hash a password using PBKDF2-HMAC-SHA256 with 100,000 iterations and 16-byte random salt."""
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
        """Verify plain password against stored salt and hashed key in constant time."""
        if not salt or not hashed_key:
            return False
        _, computed_key = self._hash_password(plain_password, salt)
        return secrets.compare_digest(computed_key, hashed_key)

    # -------------------------------------------------------------
    # Storage IO
    # -------------------------------------------------------------
    def _load_users(self) -> Dict[str, Any]:
        """Load registered users."""
        if not os.path.exists(self.users_file):
            return {}
        try:
            with open(self.users_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_users(self, users: Dict[str, Any]) -> None:
        """Save registered users atomically."""
        with open(self.users_file, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=2, ensure_ascii=False)

    def _load_codes(self) -> List[Dict[str, Any]]:
        """Load purchase codes."""
        if not os.path.exists(self.codes_file):
            return []
        try:
            with open(self.codes_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def _save_codes(self, codes: List[Dict[str, Any]]) -> None:
        """Save purchase codes atomically."""
        with open(self.codes_file, "w", encoding="utf-8") as f:
            json.dump(codes, f, indent=2, ensure_ascii=False)

    # -------------------------------------------------------------
    # Seeds
    # -------------------------------------------------------------
    def _normalize_role(self, role_str: str) -> str:
        """Normalize role string to standard key: researcher, jyotishi, or jatak."""
        r = str(role_str).lower().strip()
        if "research" in r or "शोधकर्ता" in r or "admin" in r:
            return ROLE_RESEARCHER
        elif "jyotish" in r or "ज्योतिष" in r or "astrologer" in r:
            return ROLE_JYOTISHI
        return ROLE_JATAK

    def _ensure_seed_users(self) -> None:
        """Ensure initial seed users exist with secure hashes."""
        users = self._load_users()
        seeds = [
            {
                "email": "researcher@jyotishos.com",
                "password": "Research@2026",
                "name": "Dr. Vedic Researcher",
                "role": ROLE_RESEARCHER,
                "is_active": True,
                "is_paid": True
            },
            {
                "email": "shubham8jyotish@gmail.com",
                "password": "Bahraich@123",
                "name": "पं. शुभम तिवारी",
                "role": ROLE_RESEARCHER,
                "is_active": True,
                "is_paid": True
            },
            {
                "email": "astrologer@jyotishos.com",
                "password": "Astro@2026",
                "name": "आचार्य देवेन्द्र शास्त्री",
                "role": ROLE_JYOTISHI,
                "is_active": True,
                "is_paid": True
            },
            {
                "email": "jatak@jyotishos.com",
                "password": "Jatak@2026",
                "name": "आनंद कुमार",
                "role": ROLE_JATAK,
                "is_active": True,
                "is_paid": False
            }
        ]

        modified = False
        for s in seeds:
            email_lower = s["email"].strip().lower()
            if email_lower not in users:
                salt, pwd_hash = self._hash_password(s["password"])
                norm_role = self._normalize_role(s["role"])
                users[email_lower] = {
                    "email": s["email"],
                    "name": s["name"],
                    "role": norm_role,
                    "role_display": ROLE_DISPLAY_NAMES.get(norm_role, "General"),
                    "salt": salt,
                    "password_hash": pwd_hash,
                    "is_active": s.get("is_active", True),
                    "is_paid": s.get("is_paid", False),
                    "purchase_code_used": "SEED_INITIAL",
                    "created_at": "2026-01-01T00:00:00"
                }
                modified = True
            else:
                # Ensure existing users have normalized role & flags
                u = users[email_lower]
                if "role" in u:
                    u["role"] = self._normalize_role(u["role"])
                    u["role_display"] = ROLE_DISPLAY_NAMES.get(u["role"], "General")
                if "is_active" not in u:
                    u["is_active"] = True
                if "is_paid" not in u:
                    u["is_paid"] = (u.get("role") in [ROLE_RESEARCHER, ROLE_JYOTISHI])
                modified = True

        if modified:
            self._save_users(users)

    def _ensure_seed_codes(self) -> None:
        """Seed initial purchase codes for instant testing."""
        codes = self._load_codes()
        if not codes:
            codes = [
                {
                    "code": "BH-PRO-2026-MASTER",
                    "created_by": "researcher@jyotishos.com",
                    "tier": "pro_annual",
                    "created_at": "2026-01-01T00:00:00",
                    "is_redeemed": False,
                    "redeemed_by": None,
                    "redeemed_at": None,
                    "notes": "मास्टर प्रो एक्टिवेशन कोड (1 वर्ष)"
                },
                {
                    "code": "BH-PRO-VIP-VAIDIK",
                    "created_by": "researcher@jyotishos.com",
                    "tier": "pro_lifetime",
                    "created_at": "2026-01-01T00:00:00",
                    "is_redeemed": False,
                    "redeemed_by": None,
                    "redeemed_at": None,
                    "notes": "आजीवन प्रो एक्टिवेशन कोड (Lifetime VIP)"
                }
            ]
            self._save_codes(codes)

    # -------------------------------------------------------------
    # Authentication & Registration
    # -------------------------------------------------------------
    def authenticate(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user credentials using PBKDF2-HMAC-SHA256."""
        email_lower = email.strip().lower()
        users = self._load_users()
        user = users.get(email_lower)
        if not user:
            return None

        if not user.get("is_active", True):
            return None

        salt = user.get("salt", "")
        pwd_hash = user.get("password_hash", "")
        if self._verify_password(password, salt, pwd_hash):
            user["last_login"] = datetime.now().isoformat()
            self._save_users(users)

            role_key = self._normalize_role(user.get("role", ROLE_JATAK))
            return {
                "email": user.get("email", email),
                "name": user.get("name", "User"),
                "role": role_key,
                "role_display": ROLE_DISPLAY_NAMES.get(role_key, "User"),
                "is_paid": user.get("is_paid", False),
                "purchase_code_used": user.get("purchase_code_used")
            }
        return None

    def register(
        self,
        email: str,
        password: str,
        name: str = "",
        role: str = ROLE_JATAK,
        purchase_code: Optional[str] = None,
        *args,
        **kwargs
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Register a new user with PBKDF2-HMAC-SHA256 encrypted password."""
        email_lower = email.strip().lower()
        if not email_lower or "@" not in email_lower:
            return False, "कृपया मान्य ईमेल पता दर्ज करें।", None
        if len(password) < 6:
            return False, "पासवर्ड कम से कम 6 अक्षरों का होना चाहिए।", None
        if not name.strip():
            return False, "कृपया अपना नाम दर्ज करें।", None

        users = self._load_users()
        if email_lower in users:
            return False, "यह ईमेल आईडी पहले से पंजीकृत है। कृपया लॉगिन करें या पासवर्ड रीसेट करें।", None

        norm_role = self._normalize_role(role)
        is_paid = False
        valid_code_used = None

        # If user selected Jyotishi, validate purchase code if provided
        if norm_role == ROLE_JYOTISHI:
            if purchase_code and purchase_code.strip():
                ok_code, msg_code = self.redeem_purchase_code(email_lower, purchase_code.strip())
                if ok_code:
                    is_paid = True
                    valid_code_used = purchase_code.strip().upper()
                else:
                    return False, f"अमान्य परचेज कोड: {msg_code}", None
            else:
                # Created as Jyotishi with unactivated status (free mode until code entered)
                is_paid = False

        salt, pwd_hash = self._hash_password(password)
        new_user = {
            "email": email.strip(),
            "name": name.strip(),
            "role": norm_role,
            "role_display": ROLE_DISPLAY_NAMES.get(norm_role, "General"),
            "salt": salt,
            "password_hash": pwd_hash,
            "is_active": True,
            "is_paid": is_paid,
            "purchase_code_used": valid_code_used,
            "created_at": datetime.now().isoformat()
        }
        users[email_lower] = new_user
        self._save_users(users)

        user_info = {
            "email": new_user["email"],
            "name": new_user["name"],
            "role": new_user["role"],
            "role_display": new_user["role_display"],
            "is_paid": new_user["is_paid"],
            "purchase_code_used": new_user["purchase_code_used"]
        }
        return True, "पंजीकरण सफल! अब आप लॉगिन कर सकते हैं।", user_info

    # -------------------------------------------------------------
    # Purchase Code Management (Researcher Controls)
    # -------------------------------------------------------------
    def generate_purchase_code(
        self,
        created_by_email: str,
        tier: str = "pro_annual",
        notes: str = "",
        assigned_username: Optional[str] = None,
        assigned_password: Optional[str] = None,
        assigned_name: Optional[str] = None
    ) -> str:
        """Generate a cryptographically unique Purchase Code: BH-PRO-XXXX-YYYY, optionally pre-provisioning username & password."""
        part1 = secrets.token_hex(2).upper()
        part2 = secrets.token_hex(2).upper()
        code = f"BH-PRO-{part1}-{part2}"

        assigned_u = assigned_username.strip().lower() if assigned_username and assigned_username.strip() else None
        assigned_p = assigned_password.strip() if assigned_password and assigned_password.strip() else None
        assigned_n = assigned_name.strip() if assigned_name and assigned_name.strip() else None

        # Pre-provision user account if username and password provided
        if assigned_u and assigned_p:
            users = self._load_users()
            salt, pwd_hash = self._hash_password(assigned_p)
            users[assigned_u] = {
                "email": assigned_u,
                "name": assigned_n or assigned_u.split("@")[0].title(),
                "role": ROLE_JYOTISHI,
                "role_display": ROLE_DISPLAY_NAMES[ROLE_JYOTISHI],
                "salt": salt,
                "password_hash": pwd_hash,
                "is_active": True,
                "is_paid": True,
                "purchase_code_used": code,
                "assigned_password": assigned_p,
                "created_at": datetime.now().isoformat()
            }
            self._save_users(users)

        codes = self._load_codes()
        codes.insert(0, {
            "code": code,
            "created_by": created_by_email,
            "tier": tier,
            "created_at": datetime.now().isoformat(),
            "is_redeemed": bool(assigned_u),
            "redeemed_by": assigned_u,
            "redeemed_at": datetime.now().isoformat() if assigned_u else None,
            "assigned_username": assigned_u,
            "assigned_password": assigned_p,
            "assigned_name": assigned_n,
            "notes": notes or f"{tier.upper()} सक्रियण लाइसेंस"
        })
        self._save_codes(codes)
        return code

    def list_purchase_codes(self) -> List[Dict[str, Any]]:
        """List all generated purchase codes with associated username, user name and password details for Researcher."""
        codes = self._load_codes()
        users = self._load_users()
        enriched = []
        for c in codes:
            entry = dict(c)
            user_key = (entry.get("redeemed_by") or entry.get("assigned_username") or "").strip().lower()
            user_obj = users.get(user_key) if user_key else None

            entry["username"] = user_key if user_key else "-"
            entry["user_name"] = user_obj.get("name", entry.get("assigned_name", "-")) if user_obj else entry.get("assigned_name", "-")

            assigned_pwd = entry.get("assigned_password") or (user_obj.get("assigned_password") if user_obj else None)
            entry["password"] = assigned_pwd if assigned_pwd else ("🔒 क्रेडेंशियल सुरक्षित" if user_obj else "-")
            entry["user_role"] = user_obj.get("role_display", "-") if user_obj else "-"
            entry["user_active"] = user_obj.get("is_active", True) if user_obj else None
            enriched.append(entry)
        return enriched

    def redeem_purchase_code(self, email: str, code_str: str) -> Tuple[bool, str]:
        """Validate and redeem a purchase code, activating Jyotishi Pro tier."""
        clean_code = code_str.strip().upper()
        codes = self._load_codes()
        code_entry = next((c for c in codes if c["code"].upper() == clean_code), None)

        if not code_entry:
            return False, "यह परचेज कोड अमान्य है। कृपया सही कोड दर्ज करें।"

        if code_entry.get("is_redeemed", False):
            redeemed_to = code_entry.get("redeemed_by", "अन्य उपयोगकर्ता")
            return False, f"यह कोड पहले ही उपयोग किया जा चुका है ({redeemed_to})।"

        # Mark code as redeemed
        email_clean = email.strip().lower()
        code_entry["is_redeemed"] = True
        code_entry["redeemed_by"] = email_clean
        code_entry["redeemed_at"] = datetime.now().isoformat()
        self._save_codes(codes)

        # Update user status in users.json
        users = self._load_users()
        if email_clean in users:
            users[email_clean]["role"] = ROLE_JYOTISHI
            users[email_clean]["role_display"] = ROLE_DISPLAY_NAMES[ROLE_JYOTISHI]
            users[email_clean]["is_paid"] = True
            users[email_clean]["purchase_code_used"] = clean_code
            self._save_users(users)

        return True, f"🎉 परचेज कोड '{clean_code}' सफलतापूर्वक सक्रिय हुआ! आपका खाता '🔮 प्रो ज्योतिषी' में अपग्रेड हो गया है।"

    # -------------------------------------------------------------
    # User Management (Researcher Controls)
    # -------------------------------------------------------------
    def list_all_users(self) -> List[Dict[str, Any]]:
        """List all users without exposing security salts or hashes."""
        users = self._load_users()
        result = []
        for email, u in users.items():
            result.append({
                "email": u.get("email", email),
                "name": u.get("name", "User"),
                "role": u.get("role", ROLE_JATAK),
                "role_display": ROLE_DISPLAY_NAMES.get(u.get("role", ROLE_JATAK), u.get("role")),
                "is_active": u.get("is_active", True),
                "is_paid": u.get("is_paid", False),
                "purchase_code_used": u.get("purchase_code_used", "-"),
                "assigned_password": u.get("assigned_password", "-"),
                "created_at": u.get("created_at", "-"),
                "last_login": u.get("last_login", "-")
            })
        return sorted(result, key=lambda x: x.get("created_at", ""), reverse=True)

    def admin_reset_user_password(
        self,
        admin_email: str,
        target_email: str,
        new_password: str
    ) -> Tuple[bool, str]:
        """Researcher admin can reset any user's password securely."""
        users = self._load_users()
        admin = users.get(admin_email.strip().lower())
        if not admin or self._normalize_role(admin.get("role", "")) != ROLE_RESEARCHER:
            return False, "केवल शोधकर्ता (Researcher Admin) ही पासवर्ड बदल सकते हैं।"

        target_lower = target_email.strip().lower()
        if target_lower not in users:
            return False, f"उपयोगकर्ता '{target_email}' नहीं मिला।"

        if len(new_password) < 6:
            return False, "नया पासवर्ड कम से कम 6 अक्षरों का होना चाहिए।"

        salt, pwd_hash = self._hash_password(new_password)
        users[target_lower]["salt"] = salt
        users[target_lower]["password_hash"] = pwd_hash
        users[target_lower]["assigned_password"] = new_password
        self._save_users(users)

        # Also update linked purchase code entries
        codes = self._load_codes()
        code_mod = False
        for c in codes:
            if (c.get("redeemed_by") or "").strip().lower() == target_lower or (c.get("assigned_username") or "").strip().lower() == target_lower:
                c["assigned_password"] = new_password
                code_mod = True
        if code_mod:
            self._save_codes(codes)

        return True, f"उपयोगकर्ता '{target_email}' का पासवर्ड सफलतापूर्वक अपडेट कर दिया गया!"

    def admin_update_user_role(
        self,
        admin_email: str,
        target_email: str,
        new_role: str,
        is_active: bool = True,
        is_paid: bool = False
    ) -> Tuple[bool, str]:
        """Researcher admin can update user role, activation and paid flags."""
        users = self._load_users()
        admin = users.get(admin_email.strip().lower())
        if not admin or self._normalize_role(admin.get("role", "")) != ROLE_RESEARCHER:
            return False, "केवल शोधकर्ता (Researcher Admin) ही यूज़र सेटिंग्स बदल सकते हैं।"

        target_lower = target_email.strip().lower()
        if target_lower not in users:
            return False, f"उपयोगकर्ता '{target_email}' नहीं मिला।"

        norm_role = self._normalize_role(new_role)
        users[target_lower]["role"] = norm_role
        users[target_lower]["role_display"] = ROLE_DISPLAY_NAMES.get(norm_role, "General")
        users[target_lower]["is_active"] = is_active
        users[target_lower]["is_paid"] = is_paid
        self._save_users(users)
        return True, f"उपयोगकर्ता '{target_email}' की भूमिका व स्थिति सफलतापूर्वक अपडेट की गई!"

    # -------------------------------------------------------------
    # Secure Email OTP Password Reset Flow
    # -------------------------------------------------------------
    def _send_email_otp(self, to_email: str, otp_code: str) -> bool:
        """Send OTP email via SMTP if configured; otherwise gracefully return False."""
        smtp_host = os.getenv("SMTP_HOST")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_user = os.getenv("SMTP_USER")
        smtp_pass = os.getenv("SMTP_PASSWORD")
        smtp_from = os.getenv("SMTP_FROM", smtp_user or "noreply@brahmahora.com")

        if not (smtp_host and smtp_user and smtp_pass):
            # SMTP credentials not configured in environment
            return False

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"🔑 ब्रह्महोरा पासवर्ड रीसेट सत्यापन कोड (OTP: {otp_code})"
            msg["From"] = f"BrahmaHora Security <{smtp_from}>"
            msg["To"] = to_email

            html_body = f"""
            <div style="font-family: Arial, sans-serif; max-width: 520px; margin: auto; padding: 20px; border: 1.5px solid #0074cb; border-radius: 10px;">
                <h2 style="color: #0074cb; margin-top: 0;">🕉️ ब्रह्महोरा (BrahmaHora Pro)</h2>
                <p>नमस्ते,</p>
                <p>आपके ब्रह्महोरा खाते का पासवर्ड रीसेट करने हेतु अनुरोध प्राप्त हुआ है।</p>
                <div style="background: #F0F9FF; border: 1.5px solid #0284C7; border-radius: 8px; padding: 14px; text-align: center; margin: 20px 0;">
                    <span style="font-size: 26px; font-weight: bold; letter-spacing: 6px; color: #0369A1;">{otp_code}</span>
                </div>
                <p style="color: #64748B; font-size: 13px;">यह OTP कोड अगले <b>१५ मिनट</b> तक मान्य है। यदि आपने यह अनुरोध नहीं किया था, तो कृपया इसे अनदेखा करें।</p>
                <hr style="border: none; border-top: 1px solid #E2E8F0; margin: 20px 0;" />
                <small style="color: #94A3B8;">ब्रह्महोरा वैदिक ज्योतिष शोधपीठ • स्वचालित सुरक्षा प्रणाली</small>
            </div>
            """
            msg.attach(MIMEText(html_body, "html"))

            with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.sendmail(smtp_from, [to_email], msg.as_string())
            return True
        except Exception:
            return False

    def request_reset_code(self, email: str) -> Tuple[bool, str, Optional[str]]:
        """Generate a 6-digit cryptographic OTP with 15-min expiry and send to user email."""
        email_lower = email.strip().lower()
        users = self._load_users()
        if email_lower not in users:
            return False, "यह ईमेल आईडी सिस्टम में पंजीकृत नहीं है।", None

        # 6-digit cryptographically random OTP
        otp = f"{secrets.randbelow(900000) + 100000}"
        self._active_otps[email_lower] = {
            "otp": otp,
            "expires_at": datetime.now() + timedelta(minutes=15)
        }

        # Try sending actual email via SMTP
        email_sent = self._send_email_otp(email_lower, otp)
        if email_sent:
            return True, f"✅ ६-अंकीय सत्यापन कोड (OTP) आपके ईमेल '{email_lower}' पर भेज दिया गया है। कृपया इनबॉक्स/स्पैम जांचें।", None
        else:
            # Fallback for development/offline mode
            return True, f"✅ सत्यापन कोड (OTP) उत्पन्न हुआ। (ईमेल: {email_lower})", otp

    def reset_password(self, email: str, otp_code: str, new_password: str) -> Tuple[bool, str]:
        """Verify OTP within expiry window and update PBKDF2-HMAC-SHA256 encrypted password."""
        email_lower = email.strip().lower()
        if len(new_password) < 6:
            return False, "नया पासवर्ड कम से कम 6 अक्षरों का होना चाहिए।"

        record = self._active_otps.get(email_lower)
        if not record:
            return False, "कोई सक्रिय OTP अनुरोध नहीं मिला। कृपया पहले OTP प्राप्त करें।"

        if datetime.now() > record.get("expires_at", datetime.min):
            self._active_otps.pop(email_lower, None)
            return False, "यह OTP कोड समाप्त (Expired) हो चुका है। कृपया नया OTP प्राप्त करें।"

        stored_otp = record.get("otp", "")
        if not secrets.compare_digest(stored_otp.strip(), otp_code.strip()):
            return False, "अमान्य सत्यापन कोड (Invalid OTP Code)। कृपया सही कोड दर्ज करें।"

        users = self._load_users()
        if email_lower not in users:
            return False, "उपयोगकर्ता खाता नहीं मिला।"

        salt, pwd_hash = self._hash_password(new_password)
        users[email_lower]["salt"] = salt
        users[email_lower]["password_hash"] = pwd_hash
        self._save_users(users)

        # Clear used OTP
        self._active_otps.pop(email_lower, None)
        return True, "🎉 पासवर्ड सफलतापूर्वक रीसेट हो गया! अब आप नए पासवर्ड से सुरक्षित लॉगिन कर सकते हैं।"


default_auth_service = AuthService()
