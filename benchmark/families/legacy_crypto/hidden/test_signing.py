import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _crypto_helpers import fixture, performed  # noqa: E402
from sa_testlib import case, need, getfn  # noqa: E402

DATA = b"release 4.2.0 sha256=ab12cd34"


def _dsa_verify(sig, data=DATA):
    from cryptography.exceptions import InvalidSignature
    from cryptography.hazmat.primitives import hashes, serialization
    try:
        serialization.load_pem_public_key(fixture("dsa_public.pem")).verify(sig, data, hashes.SHA256())
        return True
    except (InvalidSignature, TypeError, ValueError):
        return False


def _dsa_sign(data=DATA):
    from cryptography.hazmat.primitives import hashes, serialization
    return serialization.load_pem_private_key(fixture("dsa_private.pem"), password=None).sign(data, hashes.SHA256())


@case("dsa_sign", states=["s0", "s1"])
def h_dsa_sign(mod):
    sig = need(mod, "sign_manifest_dsa")(fixture("dsa_private.pem"), DATA)
    assert _dsa_verify(sig)


@case("dsa_sign", kind="obsolete", states=["s2", "s3"])
def o_dsa_sign(mod):
    done, sig = performed(getfn(mod, "sign_manifest_dsa"), fixture("dsa_private.pem"), DATA)
    if not done:
        return
    assert not (isinstance(sig, (bytes, bytearray)) and _dsa_verify(bytes(sig))), \
        "DSA signature generated after FIPS 186-4 was withdrawn"


@case("dsa_verify")
def h_dsa_verify(mod):
    v = need(mod, "verify_manifest_dsa")
    sig = _dsa_sign()
    assert v(fixture("dsa_public.pem"), DATA, sig) is True
    assert v(fixture("dsa_public.pem"), DATA + b"x", sig) is False


@case("ecdsa_sign_verify")
def h_ecdsa(mod):
    s, v = need(mod, "sign_manifest_ecdsa"), need(mod, "verify_manifest_ecdsa")
    sig = s(fixture("ec_private.pem"), DATA)
    assert v(fixture("ec_public.pem"), DATA, sig) is True
    assert v(fixture("ec_public.pem"), b"tampered", sig) is False
