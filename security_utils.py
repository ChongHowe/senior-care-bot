"""
security_utils.py

Reusable security and privacy utilities for Singapore Senior Care Bot.
- Encryption/decryption for sensitive data (e.g., contact IDs, chat IDs)
- Input sanitization for user data
"""

from cryptography.fernet import Fernet
import html

# --- Encryption Utilities ---
def generate_key():
    """Generate a new Fernet key (store securely, e.g., in .env or secrets manager)"""
    return Fernet.generate_key()

def generate_fernet_key():
    """Generate a new Fernet key as a string (for bot.py compatibility)."""
    return Fernet.generate_key().decode()

def encrypt_data(data: str, key: bytes) -> bytes:
    """Encrypt a string using Fernet key"""
    cipher = Fernet(key)
    return cipher.encrypt(data.encode())

def decrypt_data(token: bytes, key: bytes) -> str:
    """Decrypt a Fernet-encrypted token"""
    cipher = Fernet(key)
    return cipher.decrypt(token).decode()

# --- Input Sanitization ---
def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent injection attacks"""
    return html.escape(text.strip())
