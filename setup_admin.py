"""
Admin Panel Setup Helper

This script helps you set up the admin panel by generating a secure admin API key
and updating your .env file.
"""

import secrets
import os
from pathlib import Path


def generate_admin_key():
    """Generate a secure admin API key"""
    return secrets.token_urlsafe(32)


def update_env_file(api_key):
    """Update .env file with admin API key"""
    env_path = Path(__file__).parent / ".env"
    env_example_path = Path(__file__).parent / ".env.example"

    # Create .env from .env.example if it doesn't exist
    if not env_path.exists() and env_example_path.exists():
        print("Creating .env file from .env.example...")
        with open(env_example_path, "r") as f:
            content = f.read()
        with open(env_path, "w") as f:
            f.write(content)

    # Read current .env
    if env_path.exists():
        with open(env_path, "r") as f:
            lines = f.readlines()

        # Update or add ADMIN_API_KEY
        updated = False
        for i, line in enumerate(lines):
            if line.startswith("ADMIN_API_KEY="):
                lines[i] = f"ADMIN_API_KEY={api_key}\n"
                updated = True
                break

        if not updated:
            lines.append(f"\nADMIN_API_KEY={api_key}\n")

        # Write back
        with open(env_path, "w") as f:
            f.writelines(lines)

        print(f"✓ Updated .env file with admin API key")
    else:
        print("⚠ .env file not found. Please create it manually.")


def main():
    print("=" * 60)
    print("Admin Panel Setup Helper")
    print("=" * 60)
    print()

    # Generate key
    api_key = generate_admin_key()
    print(f"Generated Admin API Key:")
    print(f"  {api_key}")
    print()

    # Ask if user wants to update .env
    response = input("Update .env file with this key? (y/n): ").strip().lower()

    if response == "y":
        update_env_file(api_key)
        print()
        print("✓ Setup complete!")
        print()
        print("Next steps:")
        print("  1. Restart your application")
        print("  2. Navigate to http://localhost:8000/admin/ui")
        print("  3. Login with your admin API key")
    else:
        print()
        print("Please add this key to your .env file manually:")
        print(f"  ADMIN_API_KEY={api_key}")

    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
