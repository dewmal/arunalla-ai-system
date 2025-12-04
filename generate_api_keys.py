#!/usr/bin/env python3
"""Generate secure API keys"""
import secrets

def generate_api_key(length=32):
    """Generate a secure random API key"""
    return secrets.token_urlsafe(length)

if __name__ == "__main__":
    print("Generated API Keys:")
    print("-" * 50)
    for i in range(3):
        key = generate_api_key()
        print(f"Key {i+1}: {key}")
    print("-" * 50)
    print("\nAdd these to your .env file:")
    keys = [generate_api_key() for _ in range(3)]
    print(f"VALID_API_KEYS={','.join(keys)}")
    print("ALLOW_ALL_API_KEYS=false")
