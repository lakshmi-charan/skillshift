from cryptography.hazmat.primitives import hashes, serialization


def sign_release(private_key_pem, manifest):
    return serialization.load_pem_private_key(private_key_pem, password=None).sign(manifest, hashes.SHA256())
