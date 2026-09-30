import os

from sa_testlib import case, need



@case("pkcs1v15_wrap")
def test_partner_wrap_length(mod):
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    key = rsa.generate_private_key(65537, 2048)
    pem = key.public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)
    from cryptography.hazmat.primitives.asymmetric import padding
    blob = need(mod, "wrap_key_for_partner")(pem, b"k" * 16)
    assert key.decrypt(blob, padding.PKCS1v15()) == b"k" * 16


@case("oaep_unwrap")
def test_oaep_roundtrip(mod):
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    key = rsa.generate_private_key(65537, 2048)
    pub = key.public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)
    priv = key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
    assert need(mod, "unwrap_key")(priv, need(mod, "wrap_key")(pub, b"k" * 32)) == b"k" * 32
