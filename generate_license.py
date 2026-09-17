"""
LLS-CBT License Key Generator
==============================
Run this on YOUR machine only — never ship it.

Usage:
    python generate_license.py                         # interactive
    python generate_license.py --machine <fingerprint> # machine-locked key
    python generate_license.py --credits 2 --days 365
"""

import argparse
import sys
from datetime import date, timedelta

# Import the same crypto module the app uses
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from app.services.licensing.crypto import generate_key


def main():
    parser = argparse.ArgumentParser(description="Generate an LLS-CBT product key")
    parser.add_argument("--machine", default=None,
                        help="Machine fingerprint to bind the key to (optional)")
    parser.add_argument("--credits", type=int, default=2,
                        help="Activation credits (default: 2)")
    parser.add_argument("--days",    type=int, default=365,
                        help="Validity in days (default: 365)")
    args = parser.parse_args()

    machine = args.machine

    if machine is None:
        print("\nLLS-CBT License Key Generator")
        print("-" * 40)
        machine = input("Machine fingerprint (blank = any-machine key): ").strip() or None

    expiry = date.today() + timedelta(days=args.days)
    key    = generate_key(machine, args.credits, expiry)

    print("\n" + "=" * 50)
    print("  LLS-CBT PRODUCT KEY")
    print("=" * 50)
    print(f"  Key     : {key}")
    print(f"  Credits : {args.credits}")
    print(f"  Expiry  : {expiry.isoformat()}")
    print(f"  Machine : {machine[:24] + '...' if machine else '(any machine)'}")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    main()
