import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "hidden"))
from _crypto_helpers import fixture  # noqa: E402
from sa_testlib import case, need  # noqa: E402

K = bytes(range(32))


def _dec(blob):
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import padding
    priv = serialization.load_pem_private_key(fixture("rsa_private.pem"), password=None)
    return priv.decrypt(blob, padding.PKCS1v15())


@case("functional", states=["s0"])
def t_send(mod):
    assert _dec(need(mod, "send_session_key")(fixture("rsa_public.pem"), K)) == K


@case("pkcs1v15_disallowed", kind="policy", states=["s1", "s2", "s3"])
def t_refused(mod):
    f = need(mod, "send_session_key")
    try:
        blob = f(fixture("rsa_public.pem"), K)
    except PermissionError:
        return
    try:
        ok = _dec(blob) == K
    except Exception:
        ok = False
    assert not ok, "PKCS#1 v1.5 key transport performed after 2023"
