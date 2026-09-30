"""Release-manifest signatures."""
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec


def sign_manifest_dsa(private_pem, data):
    key = serialization.load_pem_private_key(private_pem, password=None)
    return key.sign(data, hashes.SHA256())


def verify_manifest_dsa(public_pem, data, signature):
    try:
        serialization.load_pem_public_key(public_pem).verify(signature, data, hashes.SHA256())
        return True
    except InvalidSignature:
        return False


def sign_manifest_ecdsa(private_pem, data):
    key = serialization.load_pem_private_key(private_pem, password=None)
    return key.sign(data, ec.ECDSA(hashes.SHA256()))


def verify_manifest_ecdsa(public_pem, data, signature):
    try:
        serialization.load_pem_public_key(public_pem).verify(signature, data, ec.ECDSA(hashes.SHA256()))
        return True
    except InvalidSignature:
        return False
