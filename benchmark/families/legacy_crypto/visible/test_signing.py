from sa_testlib import case, need


@case("dsa_sign")
def test_dsa_roundtrip(mod):
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import dsa
    key = dsa.generate_private_key(2048)
    priv = key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
    pub = key.public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)
    sig = need(mod, "sign_manifest_dsa")(priv, b"m")
    assert need(mod, "verify_manifest_dsa")(pub, b"m", sig)


@case("ecdsa_sign_verify")
def test_ecdsa_roundtrip(mod):
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import ec
    key = ec.generate_private_key(ec.SECP256R1())
    priv = key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
    pub = key.public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)
    assert need(mod, "verify_manifest_ecdsa")(pub, b"m", need(mod, "sign_manifest_ecdsa")(priv, b"m"))
