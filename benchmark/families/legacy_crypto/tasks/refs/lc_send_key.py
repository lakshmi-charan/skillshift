from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding


def send_session_key(partner_public_pem, session_key):
    return serialization.load_pem_public_key(partner_public_pem).encrypt(session_key, padding.PKCS1v15())
