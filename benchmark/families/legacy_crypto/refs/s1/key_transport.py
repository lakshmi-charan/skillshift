"""RSA key transport."""
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding


def _pub(pem):
    return serialization.load_pem_public_key(pem)


def wrap_key_for_partner(public_pem, key):
    raise PermissionError("PKCS#1 v1.5 key transport is disallowed after 2023 (NIST SP 800-131A Rev. 2)")


def wrap_key(public_pem, key):
    return _pub(public_pem).encrypt(key, padding.OAEP(mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(),
                                                      label=None))


def unwrap_key(private_pem, blob):
    priv = serialization.load_pem_private_key(private_pem, password=None)
    return priv.decrypt(blob, padding.OAEP(mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None))
