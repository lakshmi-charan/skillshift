"""Triple-DES payloads for the partner system (three-key TDEA, CBC, PKCS7)."""
import os

from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


def encrypt_for_partner(key, plaintext):
    """Return IV || ciphertext. key: 24 bytes (three-key TDEA)."""
    iv = os.urandom(8)
    padder = padding.PKCS7(64).padder()
    data = padder.update(plaintext) + padder.finalize()
    enc = Cipher(algorithms.TripleDES(key), modes.CBC(iv)).encryptor()
    return iv + enc.update(data) + enc.finalize()


def decrypt_payload(key, blob):
    """Inverse of encrypt_for_partner."""
    iv, body = blob[:8], blob[8:]
    dec = Cipher(algorithms.TripleDES(key), modes.CBC(iv)).decryptor()
    data = dec.update(body) + dec.finalize()
    unpadder = padding.PKCS7(64).unpadder()
    return unpadder.update(data) + unpadder.finalize()
