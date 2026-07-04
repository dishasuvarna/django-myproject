import base64
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from django.core.exceptions import ImproperlyConfigured


class EncryptionService:
    PREFIX = "enc:v1:"
    IV_SIZE = 12

    @staticmethod
    def encrypt(data):
        if data is None or EncryptionService.is_encrypted(data):
            return data

        iv = os.urandom(EncryptionService.IV_SIZE)
        encrypted = AESGCM(EncryptionService._key()).encrypt(
            iv,
            str(data).encode("utf-8"),
            None,
        )

        return (
            f"{EncryptionService.PREFIX}"
            f"{EncryptionService._encode(iv)}:"
            f"{EncryptionService._encode(encrypted)}"
        )

    @staticmethod
    def decrypt(data):
        if data is None or not EncryptionService.is_encrypted(data):
            return data

        try:
            _, _, iv_value, encrypted_value = data.split(":", 3)
            decrypted = AESGCM(EncryptionService._key()).decrypt(
                EncryptionService._decode(iv_value),
                EncryptionService._decode(encrypted_value),
                None,
            )
            return decrypted.decode("utf-8")
        except Exception:
            return data

    @staticmethod
    def is_encrypted(data):
        return isinstance(data, str) and data.startswith(EncryptionService.PREFIX)

    @staticmethod
    def _key():
        key = os.getenv("AES_256_KEY")

        if not key:
            raise ImproperlyConfigured("AES_256_KEY environment variable is required")

        try:
            decoded = base64.urlsafe_b64decode(key)
        except Exception as exc:
            raise ImproperlyConfigured("AES_256_KEY must be base64 encoded") from exc

        if len(decoded) != 32:
            raise ImproperlyConfigured("AES_256_KEY must decode to 32 bytes")

        return decoded

    @staticmethod
    def _encode(value):
        return base64.urlsafe_b64encode(value).decode("utf-8")

    @staticmethod
    def _decode(value):
        return base64.urlsafe_b64decode(value.encode("utf-8"))
