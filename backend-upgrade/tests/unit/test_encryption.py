"""
tests/unit/test_encryption.py

Tests for app/utils/encryption.py
Covers: encrypt/decrypt round-trip, key validation, legacy migration,
        production key enforcement, is_fernet_token detection.
"""
import os
import pytest
from types import SimpleNamespace
from unittest.mock import patch
from cryptography.fernet import Fernet, InvalidToken


# ── Fixtures ──────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def clear_fernet_cache():
    """Clear the lru_cache on _get_fernet between tests."""
    from app.utils import encryption
    encryption._get_fernet.cache_clear()
    yield
    encryption._get_fernet.cache_clear()


@pytest.fixture
def valid_key():
    return Fernet.generate_key().decode()


# ── Basic round-trip ──────────────────────────────────────────

class TestEncryptDecrypt:
    def test_round_trip_with_valid_key(self, valid_key):
        with patch.dict(os.environ, {"ENCRYPTION_KEY": valid_key}):
            from app.utils.encryption import encrypt_token, decrypt_token
            from app.utils import encryption
            encryption._get_fernet.cache_clear()

            plaintext = "hsp_test_access_token_abc123"
            ciphertext = encrypt_token(plaintext)
            assert ciphertext != plaintext
            assert decrypt_token(ciphertext) == plaintext

    def test_ciphertext_is_different_each_call(self, valid_key):
        """Fernet uses random IVs — same plaintext produces different ciphertext."""
        with patch.dict(os.environ, {"ENCRYPTION_KEY": valid_key}):
            from app.utils.encryption import encrypt_token
            from app.utils import encryption
            encryption._get_fernet.cache_clear()

            c1 = encrypt_token("same_token")
            c2 = encrypt_token("same_token")
            assert c1 != c2

    def test_decrypt_wrong_key_raises(self, valid_key):
        """Decrypting with a different key must raise InvalidToken."""
        other_key = Fernet.generate_key().decode()
        # Encrypt with key A
        fernet_a = Fernet(valid_key.encode())
        ciphertext = fernet_a.encrypt(b"secret_token").decode()
        # Decrypt with key B — must raise
        fernet_b = Fernet(other_key.encode())
        with pytest.raises(InvalidToken):
            fernet_b.decrypt(ciphertext.encode())

    def test_empty_plaintext_raises(self, valid_key):
        with patch.dict(os.environ, {"ENCRYPTION_KEY": valid_key}):
            from app.utils.encryption import encrypt_token
            from app.utils import encryption
            encryption._get_fernet.cache_clear()
            with pytest.raises(ValueError, match="empty"):
                encrypt_token("")

    def test_empty_ciphertext_raises(self, valid_key):
        with patch.dict(os.environ, {"ENCRYPTION_KEY": valid_key}):
            from app.utils.encryption import decrypt_token
            from app.utils import encryption
            encryption._get_fernet.cache_clear()
            with pytest.raises(ValueError, match="empty"):
                decrypt_token("")

    def test_unicode_token_survives_round_trip(self, valid_key):
        with patch.dict(os.environ, {"ENCRYPTION_KEY": valid_key}):
            from app.utils.encryption import encrypt_token, decrypt_token
            from app.utils import encryption
            encryption._get_fernet.cache_clear()
            token = "hsp_token_with_unicode_αβγ"
            assert decrypt_token(encrypt_token(token)) == token


# ── Key management ─────────────────────────────────────────────

class TestKeyManagement:
    def test_dev_fallback_works_in_development(self):
        """Dev fallback key should work when APP_ENV=development and no ENCRYPTION_KEY."""
        with patch.dict(os.environ, {"ENCRYPTION_KEY": "", "APP_ENV": "development"}):
            from app.utils import encryption
            encryption._get_fernet.cache_clear()
            from app.utils.encryption import encrypt_token, decrypt_token
            token = "dev_test_token"
            assert decrypt_token(encrypt_token(token)) == token

    def test_missing_key_in_production_raises(self):
        """Missing ENCRYPTION_KEY in production must raise, not silently use dev key."""
        from app.utils import encryption
        encryption._get_fernet.cache_clear()
        mock_settings = SimpleNamespace(ENCRYPTION_KEY="", is_production=True)
        with patch("app.core.config.settings", mock_settings):
            encryption._get_fernet.cache_clear()
            with pytest.raises(ValueError, match="ENCRYPTION_KEY must be set"):
                encryption._get_fernet()
        encryption._get_fernet.cache_clear()

    def test_invalid_key_format_raises(self):
        """Non-Fernet key string must raise with clear message."""
        from app.utils import encryption
        encryption._get_fernet.cache_clear()
        mock_settings = SimpleNamespace(ENCRYPTION_KEY="not-a-valid-fernet-key", is_production=False)
        with patch("app.core.config.settings", mock_settings):
            encryption._get_fernet.cache_clear()
            with pytest.raises(ValueError, match="ENCRYPTION_KEY is set but invalid"):
                encryption._get_fernet()
        encryption._get_fernet.cache_clear()

    def test_generate_key_returns_valid_fernet_key(self):
        from app.utils.encryption import generate_key
        key = generate_key()
        assert len(key) > 0
        # Should be usable as a Fernet key
        f = Fernet(key.encode())
        assert f is not None


# ── Token detection ────────────────────────────────────────────

class TestIsFernetToken:
    def test_fernet_token_detected(self, valid_key):
        with patch.dict(os.environ, {"ENCRYPTION_KEY": valid_key}):
            from app.utils import encryption
            encryption._get_fernet.cache_clear()
            from app.utils.encryption import encrypt_token, is_fernet_token
            ct = encrypt_token("test")
            assert is_fernet_token(ct) is True

    def test_legacy_xor_token_not_detected_as_fernet(self):
        """Old XOR+base64 tokens don't start with 'gAAAAA'."""
        import base64
        key = b"test" * 8  # 32 bytes
        plaintext = b"legacy_token"
        encrypted = bytes(b ^ key[i % len(key)] for i, b in enumerate(plaintext))
        legacy = base64.b64encode(encrypted).decode()
        from app.utils.encryption import is_fernet_token
        assert is_fernet_token(legacy) is False


# ── Legacy migration ───────────────────────────────────────────

class TestLegacyMigration:
    def test_migrate_legacy_token(self, valid_key):
        """migrate_legacy_token should decrypt XOR and re-encrypt with Fernet."""
        import base64
        # Create a legacy XOR-encrypted token
        secret_key = "test-secret-key-for-migration-test"
        plaintext = "original_access_token"
        key_bytes = secret_key[:32].encode().ljust(32)[:32]
        encrypted = bytes(b ^ key_bytes[i % len(key_bytes)] for i, b in enumerate(plaintext.encode()))
        legacy = base64.b64encode(encrypted).decode()

        with patch.dict(os.environ, {"ENCRYPTION_KEY": valid_key}):
            from app.utils import encryption
            encryption._get_fernet.cache_clear()
            from app.utils.encryption import migrate_legacy_token, decrypt_token, is_fernet_token
            new_ct = migrate_legacy_token(legacy, secret_key)
            assert is_fernet_token(new_ct)
            assert decrypt_token(new_ct) == plaintext
