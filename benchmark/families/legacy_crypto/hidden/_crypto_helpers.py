import os
import warnings

HERE = os.path.dirname(os.path.abspath(__file__))
KEY24 = bytes(range(1, 25))


def fixture(name):
    with open(os.path.join(HERE, "fixtures", name), "rb") as f:
        return f.read()


def tdes():
    try:
        from cryptography.hazmat.decrepit.ciphers.algorithms import TripleDES
    except ImportError:
        from cryptography.hazmat.primitives.ciphers.algorithms import TripleDES
    return TripleDES


def tdes_encrypt_ref(key, plaintext, iv=b"\x00" * 8):
    from cryptography.hazmat.primitives import padding
    from cryptography.hazmat.primitives.ciphers import Cipher, modes
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        p = padding.PKCS7(64).padder()
        d = p.update(plaintext) + p.finalize()
        e = Cipher(tdes()(key), modes.CBC(iv)).encryptor()
        return iv + e.update(d) + e.finalize()


def tdes_decrypt_ref(key, blob):
    from cryptography.hazmat.primitives import padding
    from cryptography.hazmat.primitives.ciphers import Cipher, modes
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        dec = Cipher(tdes()(key), modes.CBC(blob[:8])).decryptor()
        d = dec.update(blob[8:]) + dec.finalize()
        u = padding.PKCS7(64).unpadder()
        return u.update(d) + u.finalize()


def performed(fn, *args):
    """Return (performed, result): False if fn is absent or raises."""
    if fn is None:
        return False, None
    try:
        return True, fn(*args)
    except Exception:
        return False, None
