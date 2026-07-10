"""
app/utils/encryption.py

Production-grade token encryption using Fernet (AES-128-CBC + HMAC-SHA256).
Replaces the XOR-based MVP encryption in Phase 4.1.

Key management:
- ENCRYPTION_KEY env var holds the active Fernet key (base64-url encoded 32 bytes)
- Generate a key: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
- Falls back to a deterministic dev key when ENCRYPTION_KEY is not set
  (dev key is NOT secure — only use in local development)

Usage:
    from app.utils.encryption import encrypt_token, decrypt_token
    stored = encrypt_token(raw_access_token)
    raw    = decrypt_token(stored)
"""
import base64
import hashlib
import os
from functools import lru_cache

from cryptography.fernet import Fernet, InvalidToken

from app.core.logging import get_logger

logger = get_logger(__name__)

_DEV_KEY_SEED = b"avenor-dev-only-not-for-production-use"


@lru_cache(maxsize=1)
def _get_fernet() -> Fernet:
    """
    Return a Fernet instance using ENCRYPTION_KEY from environment.
    Cached — created once per process.
    """
    from app.core.config import settings

    raw_key = settings.ENCRYPTION_KEY

    if raw_key:
        try:
            # Validate it's a proper Fernet key
            key_bytes = raw_key.encode() if isinstance(raw_key, str) else raw_key
            return Fernet(key_bytes)
        except Exception as e:
            logger.error("invalid_encryption_key", error=str(e))
            raise ValueError(
                "ENCRYPTION_KEY is set but invalid. "
                "Generate with: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
            ) from e

    # Development fallback — deterministic but insecure
    if settings.is_production:
        raise ValueError(
            "ENCRYPTION_KEY must be set in production. "
            "Generate with: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
        )

    logger.warning(
        "using_dev_encryption_key",
        message="ENCRYPTION_KEY not set — using insecure dev key. Set ENCRYPTION_KEY for production.",
    )
    # Derive a valid 32-byte key from the seed
    digest = hashlib.sha256(_DEV_KEY_SEED).digest()
    dev_key = base64.urlsafe_b64encode(digest)
    return Fernet(dev_key)


def encrypt_token(plaintext: str) -> str:
    """
    Encrypt a plaintext token for storage.
    Returns a URL-safe base64 Fernet token string.
    Never logs the plaintext.
    """
    if not plaintext:
        raise ValueError("Cannot encrypt empty token")
    try:
        fernet = _get_fernet()
        encrypted = fernet.encrypt(plaintext.encode("utf-8"))
        return encrypted.decode("utf-8")
    except Exception as e:
        logger.error("token_encryption_failed", error=type(e).__name__)
        raise


def decrypt_token(ciphertext: str) -> str:
    """
    Decrypt a stored Fernet-encrypted token.
    Raises InvalidToken if the ciphertext is tampered or key is wrong.
    Never logs the plaintext or ciphertext.
    """
    if not ciphertext:
        raise ValueError("Cannot decrypt empty ciphertext")
    try:
        fernet = _get_fernet()
        decrypted = fernet.decrypt(ciphertext.encode("utf-8"))
        return decrypted.decode("utf-8")
    except InvalidToken as e:
        logger.error("token_decryption_failed", error="InvalidToken — key mismatch or data tampered")
        raise
    except Exception as e:
        logger.error("token_decryption_error", error=type(e).__name__)
        raise


def is_fernet_token(value: str) -> bool:
    """
    Check if a stored value looks like a Fernet token (vs the old XOR+base64).
    Fernet tokens always start with 'gAAAAA' (version byte 0x80 base64-encoded).
    Used during migration from old XOR encryption.
    """
    return value.startswith("gAAAAA")


def migrate_legacy_token(legacy_value: str, secret_key: str) -> str:
    """
    Migrate an XOR-encrypted (Phase 4.1) token to Fernet (Phase 4.2).
    Returns the new Fernet-encrypted ciphertext.
    """
    import base64
    # Decrypt with old XOR scheme
    key = secret_key[:32].encode().ljust(32)[:32]
    encrypted = base64.b64decode(legacy_value.encode())
    plaintext = bytes(b ^ key[i % len(key)] for i, b in enumerate(encrypted)).decode()
    # Re-encrypt with Fernet
    return encrypt_token(plaintext)


def generate_key() -> str:
    """Generate a new Fernet encryption key. Print and store in ENCRYPTION_KEY env var."""
    return Fernet.generate_key().decode()
