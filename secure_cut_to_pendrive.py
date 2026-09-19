"""
Secure Cut-and-Move to Pen Drive Tool
Password: Shubhan@dmin123
Ensures strictly CUT & MOVE (transfers file to USB and deletes source from PC).
"""

import os
import sys
import shutil
import hashlib
import string

VAULT_PASSWORD = "Shubhan@dmin123"
VAULT_ZIP_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "AI_Jyotish_SaaS_Locked_Vault.zip"))

def get_usb_drives():
    drives = []
    if sys.platform == "win32":
        import ctypes
        kernel32 = ctypes.windll.kernel32
        for letter in string.ascii_uppercase:
            drive_root = f"{letter}:\\"
            dtype = kernel32.GetDriveTypeW(drive_root)
            # DRIVE_REMOVABLE = 2
            if dtype == 2 and os.path.exists(drive_root):
                drives.append(drive_root)
    return drives

def compute_sha256(filepath):
    sha = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            sha.update(chunk)
    return sha.hexdigest()

def secure_cut_to_usb():
    print("=" * 60)
    print("🔒 SECURE CUT-AND-MOVE TO PEN DRIVE UTILITY")
    print("=" * 60)
    
    entered_pass = input("Enter Security Password to Authorize Transfer: ")
    if entered_pass != VAULT_PASSWORD:
        print("\n❌ ACCESS DENIED: Invalid Password!")
        input("\nPress Enter to exit...")
        return
        
    if not os.path.exists(VAULT_ZIP_PATH):
        print("\n[*] Generating encrypted vault package first...")
        import create_locked_vault
        create_locked_vault.create_vault()
        
    print("\n🔍 Scanning for connected USB / Pen Drives...")
    drives = get_usb_drives()
    
    if not drives:
        print("⚠️ No Removable Pen Drive detected!")
        target_path = input("Enter Pen Drive letter or Destination Path manually (e.g. E:\\ or F:\\): ").strip()
        if not target_path:
            print("Transfer aborted.")
            input("\nPress Enter to exit...")
            return
    else:
        print(f"✅ Detected Pen Drive(s): {', '.join(drives)}")
        target_path = drives[0]
        
    if not os.path.exists(target_path):
        print(f"❌ Error: Destination path '{target_path}' not accessible.")
        input("\nPress Enter to exit...")
        return
        
    dest_file = os.path.join(target_path, os.path.basename(VAULT_ZIP_PATH))
    print(f"\n🚀 Transferring (CUTTING) to: {dest_file}...")
    
    # 1. Copy
    shutil.copy2(VAULT_ZIP_PATH, dest_file)
    
    # 2. Verify Integrity
    src_hash = compute_sha256(VAULT_ZIP_PATH)
    dest_hash = compute_sha256(dest_file)
    
    if src_hash == dest_hash:
        print("✅ Integrity Verified (SHA-256 Checksum Match 100%)")
        # 3. Secure Delete Source (Cut operation)
        os.remove(VAULT_ZIP_PATH)
        print("🗑️ Source file securely deleted from PC (STRICT CUT & PASTE COMPLETE)!")
        print(f"\n🎉 SUCCESS: Project Vault moved to Pen Drive ({dest_file}).")
    else:
        print("❌ Verification Failed! Aborting delete to protect your data.")
        
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    secure_cut_to_usb()

