import warnings
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


def read_archived_payload(key, blob):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        d = Cipher(algorithms.TripleDES(key), modes.CBC(blob[:8])).decryptor()
        data = d.update(blob[8:]) + d.finalize()
    u = padding.PKCS7(64).unpadder()
    return u.update(data) + u.finalize()
