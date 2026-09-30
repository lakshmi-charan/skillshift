import os
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


def build_partner_payload(key, settlement):
    iv = os.urandom(8)
    p = padding.PKCS7(64).padder()
    d = p.update(settlement) + p.finalize()
    e = Cipher(algorithms.TripleDES(key), modes.CBC(iv)).encryptor()
    return iv + e.update(d) + e.finalize()
