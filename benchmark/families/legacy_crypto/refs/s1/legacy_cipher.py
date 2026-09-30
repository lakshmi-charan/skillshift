"""Triple-DES payloads: decryption of legacy data only (SP 800-131A Rev. 2: encryption disallowed after 2023)."""
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


def encrypt_for_partner(key, plaintext):
    raise PermissionError("three-key TDEA encryption is disallowed after 2023 (NIST SP 800-131A Rev. 2)")


def decrypt_payload(key, blob):
    iv, body = blob[:8], blob[8:]
    dec = Cipher(algorithms.TripleDES(key), modes.CBC(iv)).decryptor()
    data = dec.update(body) + dec.finalize()
    unpadder = padding.PKCS7(64).unpadder()
    return unpadder.update(data) + unpadder.finalize()
