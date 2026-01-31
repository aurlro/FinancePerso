"""
Tests for encryption module.
"""

import pytest
import os
from modules.encryption import (
    FieldEncryption,
    encrypt_field,
    decrypt_field,
    generate_encryption_key,
    EncryptedFieldMixin,
)


class TestFieldEncryption:
    """Test FieldEncryption class."""
    
    def test_encryption_decryption(self):
        """Test basic encryption and decryption."""
        enc = FieldEncryption("test_secret_key_12345")
        
        plaintext = "sensitive data"
        encrypted = enc.encrypt(plaintext)
        
        # Encrypted value should be different and have ENC: prefix
        assert encrypted != plaintext
        assert encrypted.startswith("ENC:")
        
        # Decrypt and verify
        decrypted = enc.decrypt(encrypted)
        assert decrypted == plaintext
    
    def test_encryption_disabled_without_key(self):
        """Test that encryption is disabled without key."""
        # Clear any existing encryption key
        original_key = os.getenv('ENCRYPTION_KEY')
        if 'ENCRYPTION_KEY' in os.environ:
            del os.environ['ENCRYPTION_KEY']
        
        enc = FieldEncryption(None)
        
        # Without key, encryption should return plaintext
        plaintext = "test data"
        result = enc.encrypt(plaintext)
        assert result == plaintext
        
        # Restore key
        if original_key:
            os.environ['ENCRYPTION_KEY'] = original_key
    
    def test_decrypt_plaintext(self):
        """Test decrypting non-encrypted value."""
        enc = FieldEncryption("test_secret_key_12345")
        
        # Should return as-is
        plaintext = "not encrypted"
        result = enc.decrypt(plaintext)
        assert result == plaintext
    
    def test_decrypt_none(self):
        """Test decrypting None."""
        enc = FieldEncryption("test_secret_key_12345")
        
        result = enc.decrypt(None)
        assert result is None
    
    def test_encrypt_none(self):
        """Test encrypting None."""
        enc = FieldEncryption("test_secret_key_12345")
        
        result = enc.encrypt(None)
        assert result is None
    
    def test_is_enabled(self):
        """Test is_enabled method."""
        enc_with_key = FieldEncryption("test_key")
        assert enc_with_key.is_enabled()
        
        enc_without_key = FieldEncryption(None)
        assert not enc_without_key.is_enabled()


class TestHelperFunctions:
    """Test helper functions."""
    
    def test_generate_encryption_key(self):
        """Test key generation."""
        key = generate_encryption_key()
        
        # Should be a string
        assert isinstance(key, str)
        
        # Should be valid base64
        import base64
        decoded = base64.urlsafe_b64decode(key.encode())
        assert len(decoded) == 32  # 256 bits
    
    def test_encrypt_decrypt_helpers(self):
        """Test encrypt_field and decrypt_field helpers."""
        # Set up encryption
        os.environ['ENCRYPTION_KEY'] = 'test_encryption_key_for_helpers'
        
        plaintext = "test data"
        encrypted = encrypt_field(plaintext)
        
        assert encrypted != plaintext
        assert encrypted.startswith("ENC:")
        
        decrypted = decrypt_field(encrypted)
        assert decrypted == plaintext


class TestEncryptedFieldMixin:
    """Test EncryptedFieldMixin."""
    
    def test_encrypt_fields(self):
        """Test encrypting fields in dict."""
        os.environ['ENCRYPTION_KEY'] = 'test_key_for_mixin'
        
        mixin = EncryptedFieldMixin()
        
        data = {
            'id': 1,
            'label': 'Test',
            'notes': 'sensitive note',
            'beneficiary': 'John Doe',
            'amount': 100.0
        }
        
        encrypted = mixin.encrypt_fields(data)
        
        # Non-encrypted fields should remain unchanged
        assert encrypted['id'] == 1
        assert encrypted['label'] == 'Test'
        assert encrypted['amount'] == 100.0
        
        # Encrypted fields should have ENC: prefix
        assert encrypted['notes'].startswith('ENC:')
        assert encrypted['beneficiary'].startswith('ENC:')
    
    def test_decrypt_fields(self):
        """Test decrypting fields in dict."""
        os.environ['ENCRYPTION_KEY'] = 'test_key_for_mixin'
        
        mixin = EncryptedFieldMixin()
        
        # First encrypt
        data = {
            'notes': 'sensitive note',
            'beneficiary': 'John Doe'
        }
        encrypted = mixin.encrypt_fields(data)
        
        # Then decrypt
        decrypted = mixin.decrypt_fields(encrypted)
        
        assert decrypted['notes'] == 'sensitive note'
        assert decrypted['beneficiary'] == 'John Doe'


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_wrong_decryption_key(self):
        """Test decryption with wrong key."""
        enc1 = FieldEncryption("key_one_12345")
        enc2 = FieldEncryption("key_two_12345")
        
        plaintext = "secret"
        encrypted = enc1.encrypt(plaintext)
        
        # Decrypting with wrong key should return original encrypted value
        result = enc2.decrypt(encrypted)
        assert result == encrypted
    
    def test_empty_string(self):
        """Test encrypting empty string."""
        enc = FieldEncryption("test_key")
        
        encrypted = enc.encrypt("")
        decrypted = enc.decrypt(encrypted)
        
        assert decrypted == ""
    
    def test_unicode(self):
        """Test encrypting unicode characters."""
        enc = FieldEncryption("test_key")
        
        plaintext = "日本語テスト émojis 🎉"
        encrypted = enc.encrypt(plaintext)
        decrypted = enc.decrypt(encrypted)
        
        assert decrypted == plaintext
