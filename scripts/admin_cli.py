#!/usr/bin/env python3
"""
Admin CLI for JyotishOS (P0-T2).
Allows administrative management of licence purchase codes and users without hardcoding secrets in git.
Usage:
    python scripts/admin_cli.py create-code --tier pro_annual --admin admin@jyotishos.com --notes "Annual client license"
    python scripts/admin_cli.py list-codes
    python scripts/admin_cli.py list-users
"""

import sys
import os
import argparse

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.jyotish.services.auth import default_auth_service


def main():
    parser = argparse.ArgumentParser(description="JyotishOS Admin Security & Licence CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # create-code
    create_parser = subparsers.add_parser("create-code", help="Generate a new hashed purchase code")
    create_parser.add_argument("--tier", default="pro_annual", choices=["pro_annual", "pro_lifetime"], help="Licence tier")
    create_parser.add_argument("--admin", default="admin@jyotishos.com", help="Admin email creating code")
    create_parser.add_argument("--notes", default="Generated via Admin CLI", help="Notes or description")
    create_parser.add_argument("--assigned-user", default=None, help="Pre-provisioned user email")
    create_parser.add_argument("--assigned-pass", default=None, help="Pre-provisioned password")

    # list-codes
    subparsers.add_parser("list-codes", help="List all purchase codes")

    # list-users
    subparsers.add_parser("list-users", help="List all registered users")

    args = parser.parse_args()

    if args.command == "create-code":
        code = default_auth_service.generate_purchase_code(
            created_by_email=args.admin,
            tier=args.tier,
            notes=args.notes,
            assigned_username=args.assigned_user,
            assigned_password=args.assigned_pass
        )
        print(f"Generated licence code: {code}")
        print(f"Tier: {args.tier} | Created by: {args.admin}")

    elif args.command == "list-codes":
        codes = default_auth_service.list_purchase_codes()
        print(f"Total licence codes: {len(codes)}")
        for c in codes:
            status = "REDEEMED" if c.get("is_redeemed") else "ACTIVE"
            print(f"- [{status}] {c.get('code')} ({c.get('tier')}) -> User: {c.get('username')}")

    elif args.command == "list-users":
        users = default_auth_service.list_all_users()
        print(f"Total registered users: {len(users)}")
        for u in users:
            print(f"- {u.get('email')} | Role: {u.get('role_display')} | Paid: {u.get('is_paid')}")


if __name__ == "__main__":
    main()
