"""
Creates an AES-256 Password-Protected Archive for AI Jyotish SaaS Project.
Password: Shubhan@dmin123
"""

import os
import pyzipper

VAULT_PASSWORD = b"Shubhan@dmin123"
OUTPUT_ZIP = "../AI_Jyotish_SaaS_Locked_Vault.zip"

EXCLUDE_DIRS = {"__pycache__", ".git", ".pytest_cache", ".venv", "venv", "scratch"}
EXCLUDE_FILES = {"saved_charts_test_db.json"}

def create_vault():
    print("[*] Creating AES-256 Encrypted Project Vault...")
    total_files = 0
    
    with pyzipper.AESZipFile(
        OUTPUT_ZIP,
        'w',
        compression=pyzipper.ZIP_DEFLATED,
        encryption=pyzipper.WZ_AES
    ) as zf:
        zf.setpassword(VAULT_PASSWORD)
        zf.setencryption(pyzipper.WZ_AES, nbits=256)
        
        for root, dirs, files in os.walk("."):
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            for file in files:
                if file in EXCLUDE_FILES or file.endswith(".pyc") or file.endswith(".zip"):
                    continue
                file_path = os.path.join(root, file)
                arcname = os.path.normpath(file_path)
                zf.write(file_path, arcname)
                total_files += 1
                
    print(f"[OK] Vault created successfully: {os.path.abspath(OUTPUT_ZIP)}")
    print(f"[OK] Total Files Encrypted: {total_files}")
    print(f"[OK] Encryption: AES-256 Military Grade")
    print(f"[OK] Password: Shubhan@dmin123")

if __name__ == "__main__":
    create_vault()
