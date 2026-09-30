"""AES-256-GCM record encryption (nonce || ciphertext+tag)."""
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def encrypt_record(key, data, aad=b""):
    nonce = os.urandom(12)
    return nonce + AESGCM(key).encrypt(nonce, data, aad)


def decrypt_record(key, blob, aad=b""):
    return AESGCM(key).decrypt(blob[:12], blob[12:], aad)
