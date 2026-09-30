import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "hidden"))
from _crypto_helpers import fixture  # noqa: E402
from sa_testlib import case, need  # noqa: E402

DATA = b"manifest: app 5.1.0"


def _verify(sig):
    from cryptography.exceptions import InvalidSignature
    from cryptography.hazmat.primitives import hashes, serialization
    try:
        serialization.load_pem_public_key(fixture("dsa_public.pem")).verify(sig, DATA, hashes.SHA256())
        return True
    except (InvalidSignature, TypeError, ValueError):
        return False


@case("functional", states=["s0", "s1"])
def t_sign(mod):
    assert _verify(need(mod, "sign_release")(fixture("dsa_private.pem"), DATA))


@case("dsa_generation_not_approved", kind="policy", states=["s2", "s3"])
def t_refused(mod):
    f = need(mod, "sign_release")
    try:
        sig = f(fixture("dsa_private.pem"), DATA)
    except PermissionError:
        return
    assert not (isinstance(sig, (bytes, bytearray)) and _verify(bytes(sig))), "DSA signature generated"
