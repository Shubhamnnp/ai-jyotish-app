#!/usr/bin/env bash
# Shell Verification Script for JyotishOS (Phase U0, Task U0-T4)
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

python3 scripts/verify.py
