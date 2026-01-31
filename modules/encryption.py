"""
Encryption module for FinancePerso.
Provides AES-256 encryption for sensitive data fields.
Uses Fernet symmetric encryption with key derivation.
"""

import os
import base64
import logging
from typing import Optional, Union
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

from modules.logger import logger


class FieldEncryption:
    """
    Handles encryption and decryption of sensitive data fields.
    Uses AES-256 in CBC mode via Fernet.
    """
    
    def __init__(self, master_key: Optional[str] = None):
        """
        Initialize encryption with a master key.
        
        Args:
            master_key: The master encryption key. If None, reads from ENCRYPTION_KEY env var.
        """
        if master_key is None:
            master_key = os.getenv('ENCRYPTION_KEY')
        
        if not master_key:
            logger.warning("No encryption key provided. Encryption disabled.")
            self._cipher = None
            return
        
        try:
            # Derive a proper Fernet key from the master key
            self._cipher = self._create_cipher(master_key)
            logger.info("Field encryption initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize encryption: {e}")
            self._cipher = None
    
    def _create_cipher(self, master_key: str) -> Fernet:
        """
        Create a Fernet cipher from master key using PBKDF2.
        
        Args:
            master_key: The master key string
            
        Returns:
            Fernet cipher instance
        """
        # Use a fixed salt (in production, store salt separately)
        salt = b'financeperso_salt_v1'
        
        # Derive 32-byte key using PBKDF2
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(master_key.encode()))
        return Fernet(key)
    
    def is_enabled(self) -> bool:
        """Check if encryption is enabled and working."""
        return self._cipher is not None
    
    def encrypt(self, plaintext: Union[str, None]) -> Optional[str]:
        """
        Encrypt a string value.
        
        Args:
            plaintext: The string to encrypt
            
        Returns:
            Encrypted string (base64) or None if encryption disabled
            
        Example:
            >>> enc = FieldEncryption("my_secret_key")
            >>> encrypted = enc.encrypt("sensitive data")
        """
        if not self._cipher:
            return plaintext
        
        if plaintext is None:
            return None
        
        if not isinstance(plaintext, str):
            plaintext = str(plaintext)
        
        try:
            encrypted = self._cipher.encrypt(plaintext.encode())
            return f"ENC:{encrypted.decode()}"
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            return plaintext
    
    def decrypt(self, ciphertext: Union[str, None]) -> Optional[str]:
        """
        Decrypt an encrypted string value.
        
        Args:
            ciphertext: The encrypted string (with ENC: prefix)
            
        Returns:
            Decrypted string or original value if not encrypted
            
        Example:
            >>> enc = FieldEncryption("my_secret_key")
            >>> decrypted = enc.decrypt("ENC:...")
        """
        if not self._cipher:
            return ciphertext
        
        if ciphertext is None:
            return None
        
        # Check if value is encrypted (has ENC: prefix)
        if not isinstance(ciphertext, str) or not ciphertext.startswith('ENC:'):
            return ciphertext
        
        try:
            encrypted_data = ciphertext[4:].encode()  # Remove ENC: prefix
            decrypted = self._cipher.decrypt(encrypted_data)
            return decrypted.decode()
        except InvalidToken:
            logger.warning("Invalid encryption token - possibly wrong key")
            return ciphertext
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return ciphertext
    
    def rotate_key(self, new_master_key: str, encrypted_value: str) -> str:
        """
        Re-encrypt a value with a new key.
        
        Args:
            new_master_key: The new master key
            encrypted_value: Currently encrypted value
            
        Returns:
            Re-encrypted value with new key
        """
        # Decrypt with old key
        plaintext = self.decrypt(encrypted_value)
        
        # Create new cipher
        new_cipher = self._create_cipher(new_master_key)
        
        # Re-encrypt
        if plaintext is None:
            return None
        
        encrypted = new_cipher.encrypt(plaintext.encode())
        return f"ENC:{encrypted.decode()}"


# Singleton instance
_encryption_instance = None

def get_encryption() -> FieldEncryption:
    """Get singleton encryption instance."""
    global _encryption_instance
    if _encryption_instance is None:
        _encryption_instance = FieldEncryption()
    return _encryption_instance


def encrypt_field(value: Union[str, None]) -> Optional[str]:
    """Encrypt a field value using singleton instance."""
    return get_encryption().encrypt(value)


def decrypt_field(value: Union[str, None]) -> Optional[str]:
    """Decrypt a field value using singleton instance."""
    return get_encryption().decrypt(value)


def is_encryption_enabled() -> bool:
    """Check if encryption is enabled."""
    return get_encryption().is_enabled()


class EncryptedFieldMixin:
    """
    Mixin for database models with encrypted fields.
    Automatically encrypts/decrypts specified fields.
    """
    
    ENCRYPTED_FIELDS = ['notes', 'beneficiary']
    
    def __init__(self):
        self._encryption = get_encryption()
    
    def encrypt_fields(self, data: dict) -> dict:
        """
        Encrypt all configured fields in data dict.
        
        Args:
            data: Dictionary with field values
            
        Returns:
            Dictionary with encrypted values
        """
        if not self._encryption.is_enabled():
            return data
        
        result = data.copy()
        for field in self.ENCRYPTED_FIELDS:
            if field in result and result[field] is not None:
                result[field] = self._encryption.encrypt(result[field])
        
        return result
    
    def decrypt_fields(self, data: dict) -> dict:
        """
        Decrypt all configured fields in data dict.
        
        Args:
            data: Dictionary with field values
            
        Returns:
            Dictionary with decrypted values
        """
        if not self._encryption.is_enabled():
            return data
        
        result = data.copy()
        for field in self.ENCRYPTED_FIELDS:
            if field in result and result[field] is not None:
                result[field] = self._encryption.decrypt(result[field])
        
        return result


def generate_encryption_key() -> str:
    """
    Generate a new secure encryption key.
    
    Returns:
        Base64-encoded key string
        
    Example:
        >>> key = generate_encryption_key()
        >>> print(f"Add to .env: ENCRYPTION_KEY={key}")
    """
    key = Fernet.generate_key()
    return key.decode()


def migrate_to_encryption(db_connection, fields_to_encrypt=None):
    """
    Migrate existing database fields to encrypted format.
    
    Args:
        db_connection: Database connection
        fields_to_encrypt: List of field names to encrypt (default: notes, beneficiary)
    """
    if fields_to_encrypt is None:
        fields_to_encrypt = ['notes', 'beneficiary']
    
    encryption = get_encryption()
    
    if not encryption.is_enabled():
        logger.warning("Encryption not enabled, skipping migration")
        return
    
    cursor = db_connection.cursor()
    
    for field in fields_to_encrypt:
        logger.info(f"Migrating field: {field}")
        
        # Get all non-encrypted values
        cursor.execute(f"SELECT id, {field} FROM transactions WHERE {field} IS NOT NULL AND {field} NOT LIKE 'ENC:%'")
        rows = cursor.fetchall()
        
        if not rows:
            logger.info(f"No values to encrypt for field: {field}")
            continue
        
        # Encrypt each value
        updated = 0
        for row_id, value in rows:
            encrypted = encryption.encrypt(value)
            if encrypted != value:  # Only update if actually encrypted
                cursor.execute(
                    f"UPDATE transactions SET {field} = ? WHERE id = ?",
                    (encrypted, row_id)
                )
                updated += 1
        
        db_connection.commit()
        logger.info(f"Encrypted {updated} values for field: {field}")


__all__ = [
    'FieldEncryption',
    'get_encryption',
    'encrypt_field',
    'decrypt_field',
    'is_encryption_enabled',
    'EncryptedFieldMixin',
    'generate_encryption_key',
    'migrate_to_encryption',
]
