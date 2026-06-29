from datetime import datetime, timedelta
from typing import Optional, Any
import jwt
from jwt import PyJWTError as JWTError
from cryptography.fernet import Fernet
import logging

from app.config.settings import settings

logger = logging.getLogger("security")

import bcrypt

# Hashing helper methods
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies that a plain text password matches the stored bcrypt hash."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    """Computes a bcrypt hash for the provided password."""
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


# JWT helper methods
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Generates a secure JSON Web Token for user sessions."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    """Decodes and validates a JWT token. Returns payload dict or None if invalid."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError as e:
        logger.warning(f"Failed to decode access token: {str(e)}")
        return None


# AES-256 Token Encryption methods (Fernet)
def encrypt_token(plain_token: str) -> str:
    """Encrypts a WhatsApp access token to safely store in the database."""
    if not plain_token:
        return ""
    try:
        f = Fernet(settings.resolved_encryption_key)
        encrypted_bytes = f.encrypt(plain_token.encode("utf-8"))
        return encrypted_bytes.decode("utf-8")
    except Exception as e:
        logger.error(f"Error encrypting access token: {str(e)}", exc_info=True)
        raise RuntimeError("Token encryption failed.")

def decrypt_token(encrypted_token: str) -> str:
    """Decrypts a WhatsApp access token for outbound API client authorization."""
    if not encrypted_token:
        return ""
    try:
        f = Fernet(settings.resolved_encryption_key)
        decrypted_bytes = f.decrypt(encrypted_token.encode("utf-8"))
        return decrypted_bytes.decode("utf-8")
    except Exception as e:
        logger.error(f"Error decrypting access token: {str(e)}", exc_info=True)
        raise RuntimeError("Token decryption failed.")
