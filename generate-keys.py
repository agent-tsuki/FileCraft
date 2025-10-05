#!/usr/bin/env python3
"""
Generate secure keys for Railway environment variables
"""
import secrets
import string

def generate_secure_key(length=32):
    """Generate a secure random key"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def main():
    print("🔐 Secure Key Generator for Railway")
    print("=" * 40)
    print()
    
    secret_key = generate_secure_key(32)
    jwt_secret = generate_secure_key(32)
    
    print("Copy these to your Railway environment variables:")
    print()
    print(f"SECRET_KEY={secret_key}")
    print(f"JWT_SECRET_KEY={jwt_secret}")
    print()
    print("⚠️  Keep these keys secure and never commit them to git!")

if __name__ == "__main__":
    main()