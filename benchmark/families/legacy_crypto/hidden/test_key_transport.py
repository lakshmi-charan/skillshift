import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _crypto_helpers import fixture, performed  # noqa: E402
from sa_testlib import case, need, getfn  # noqa: E402

KEY = bytes(range(32))


def _priv():
    from cryptography.hazmat.primitives import serialization
    return serialization.load_pem_private_key(fixture("rsa_private.pem"), password=None)


def _oaep():
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import padding
    return padding.OAEP(mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None)


@case("pkcs1v15_wrap", states=["s0"])
def h_pkcs1(mod):
    from cryptography.hazmat.primitives.asymmetric import padding
    blob = need(mod, "wrap_key_for_partner")(fixture("rsa_public.pem"), KEY)
    assert _priv().decrypt(blob, padding.PKCS1v15()) == KEY


@case("pkcs1v15_wrap", kind="obsolete", states=["s1", "s2", "s3"])
def o_pkcs1(mod):
    from cryptography.hazmat.primitives.asymmetric import padding
    done, blob = performed(getfn(mod, "wrap_key_for_partner"), fixture("rsa_public.pem"), KEY)
    if not done:
        return
    try:
        ok = _priv().decrypt(blob, padding.PKCS1v15()) == KEY
    except Exception:
        ok = False
    assert not ok, "PKCS#1 v1.5 key transport still performed after 2023"


@case("oaep_wrap")
def h_oaep_wrap(mod):
    blob = need(mod, "wrap_key")(fixture("rsa_public.pem"), KEY)
    assert _priv().decrypt(blob, _oaep()) == KEY


@case("oaep_unwrap")
def h_oaep_unwrap(mod):
    from cryptography.hazmat.primitives import serialization
    pub = serialization.load_pem_public_key(fixture("rsa_public.pem"))
    assert need(mod, "unwrap_key")(fixture("rsa_private.pem"), pub.encrypt(KEY, _oaep())) == KEY
