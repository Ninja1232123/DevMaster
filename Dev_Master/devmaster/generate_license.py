#!/usr/bin/env python3
"""
License Key Generator for DevMaster Pro

Usage:
  python generate_license.py pro               # Generate one Pro key
  python generate_license.py pro 10            # Generate 10 Pro keys
  python generate_license.py team [email]      # Generate Team key
"""

import hashlib
import random
import string
import sys


def generate_random_part(length=6):
    """Generate random alphanumeric string."""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


def generate_checksum(data: str) -> str:
    """Generate checksum for license key."""
    return hashlib.sha256(data.encode()).hexdigest()[:6].upper()


def generate_license_key(tier: str) -> str:
    """
    Generate a license key.

    Format: DM-{TIER}-{RANDOM}-{CHECKSUM}
    Example: DM-PRO-ABC123-XYZ789
    """
    tier = tier.upper()

    if tier not in ["PRO", "TEAM", "ENTERPRISE"]:
        raise ValueError(f"Invalid tier: {tier}. Use: pro, team, or enterprise")

    random_part = generate_random_part(6)
    prefix_data = f"DM-{tier}-{random_part}"
    checksum = generate_checksum(prefix_data)

    return f"{prefix_data}-{checksum}"


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_license.py <tier> [count]")
        print("  tier: pro, team, or enterprise")
        print("  count: number of keys to generate (default: 1)")
        print()
        print("Examples:")
        print("  python generate_license.py pro")
        print("  python generate_license.py pro 10")
        print("  python generate_license.py team")
        sys.exit(1)

    tier = sys.argv[1]
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 1

    print(f"\n🔑 Generating {count} DevMaster {tier.upper()} license key(s)...\n")

    keys = []
    for i in range(count):
        key = generate_license_key(tier)
        keys.append(key)
        print(f"{i+1}. {key}")

    print(f"\n✅ Generated {count} license key(s)")
    print("\n📋 Email Template:")
    print("-" * 60)
    print(f"""
Subject: Your DevMaster Pro License Key

Hi there!

Thank you for purchasing DevMaster Pro! 🎉

Here's your license key:

    {keys[0]}

To activate:

1. Install DevMaster:
   pip install -e devmaster

2. Activate your license:
   devmaster activate {keys[0]}

3. Start using Pro features:
   devmaster status

Questions? Reply to this email!

Best,
DevMaster Team
""")
    print("-" * 60)

    # Save to file
    filename = f"licenses_{tier.lower()}_{count}.txt"
    with open(filename, 'w') as f:
        f.write(f"DevMaster {tier.upper()} License Keys\n")
        f.write("=" * 60 + "\n")
        f.write(f"Generated: {count} keys\n")
        f.write("=" * 60 + "\n\n")
        for i, key in enumerate(keys, 1):
            f.write(f"{i}. {key}\n")

    print(f"\n💾 Keys saved to: {filename}")


if __name__ == "__main__":
    main()
