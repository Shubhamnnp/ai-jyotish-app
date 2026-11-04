# JyotishOS — Security Credential Rotation & History Purging Guide

**Target Audience:** Repository Owner (Shubham)  
**Reference:** `docs/IMPLEMENTATION_PRD.md` (Phase 0: Task P0-T3)  
**Status:** REQUIRED ACTION POST-PHASE 0

---

## 1. Why Credential Rotation & History Purge is Necessary

Prior commits to the repository contained:
1. `data/users.json` (email addresses, legacy salt and password hashes).
2. `data/purchase_codes.json` (legacy licence codes such as `BH-PRO-2026-MASTER`).
3. `data/jyotish_enterprise.db` (SQLite database containing historical user and rule data).

While these files have been removed from the git index (`git rm --cached`) and added to `.gitignore` in **P0-T1**, **historical git commits still contain these strings**.

> [!CAUTION]
> The automated AI Agent is strictly prohibited by non-negotiable rules from rewriting Git history itself. The repository owner must execute the history purge manually using the sanctioned tools below.

---

## 2. Step 1: Rotate All Passwords and API Secrets

Immediately rotate and update the following keys in your private environment and production hosts:

1. **Google Gemini API Key (`GEMINI_API_KEY`)**:
   - Go to Google AI Studio (`https://aistudio.google.com/app/apikey`).
   - Revoke existing keys and generate a new secret key.
   - Update your local `.env` and production deployment secrets.

2. **JWT Secret Key (`JWT_SECRET`)**:
   - Generate a strong 256-bit cryptographically secure key:
     ```bash
     python -c "import secrets; print(secrets.token_hex(32))"
     ```
   - Update in `.env` / production container environment.

3. **Database Credentials (`DATABASE_URL`)**:
   - Update Postgres password for `jyotish_admin` in production.

4. **SMTP Email Credentials**:
   - Rotate `SMTP_PASSWORD` if email OTP was configured with an active mail server.

---

## 3. Step 2: Purge Git History (Owner Action)

Use either `git-filter-repo` (recommended by Git) or `BFG Repo-Cleaner` to purge sensitive files and strings from git history.

### Option A: Using `git-filter-repo` (Recommended)

1. **Install git-filter-repo**:
   ```bash
   pip install git-filter-repo
   ```

2. **Create a fresh clone backup before proceeding**:
   ```bash
   cd ..
   git clone --mirror https://github.com/Shubhamnnp/ai-jyotish-app.git ai-jyotish-backup.git
   ```

3. **Run git-filter-repo to scrub sensitive paths**:
   ```bash
   git filter-repo --path data/jyotish_enterprise.db --invert-paths --force
   git filter-repo --path data/users.json --invert-paths --force
   git filter-repo --path data/purchase_codes.json --invert-paths --force
   git filter-repo --path saved_charts_db.json --invert-paths --force
   ```

4. **Replace specific sensitive words (e.g., MASTER code string)**:
   Create a text file `replace.txt`:
   ```text
   BH-PRO-2026-MASTER==>BH-PRO-PURGED-KEY
   ```
   Run:
   ```bash
   git filter-repo --replace-text replace.txt --force
   ```

5. **Force push to GitHub**:
   ```bash
   git push origin --force --all
   git push origin --force --tags
   ```

---

### Option B: Using BFG Repo-Cleaner

1. Download `bfg.jar` from `https://rtyley.github.io/bfg-repo-cleaner/`.
2. Run:
   ```bash
   java -jar bfg.jar --delete-files "{jyotish_enterprise.db,users.json,purchase_codes.json}"
   git reflog expire --expire=now --all && git gc --prune=now --aggressive
   git push origin --force --all
   ```

---

## 4. Step 3: Invalidate & Reissue Licence Codes

1. Run the new Admin CLI to inspect active codes:
   ```bash
   python scripts/admin_cli.py list-codes
   ```
2. Generate fresh, SHA-256 hashed activation codes for verified users:
   ```bash
   python scripts/admin_cli.py create-code --tier pro_annual --admin admin@jyotishos.com --notes "Reissued client code"
   ```
3. Old plaintext legacy codes found in git history are permanently invalidated.
