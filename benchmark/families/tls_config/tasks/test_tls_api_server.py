import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "hidden"))
from _policy import profile  # noqa: E402
from _tlsutil import CERT, KEY, client_context, handshake_ok, pre13_ciphers, make_server  # noqa: E402
from sa_testlib import case, need, STATE  # noqa: E402

P = profile(STATE, "intermediate")


def _ctx(mod):
    return make_server(need(mod, "make_api_server_context"), CERT, KEY)


@case("functional")
def t_browsers_and_tls12(mod):
    ctx = _ctx(mod)
    r13 = handshake_ok(ctx, client_context())
    r12 = handshake_ok(ctx, client_context("TLSv1.2"))
    assert r13 is not None and r13[0] == "TLSv1.3", r13
    assert r12 is not None and r12[0] == "TLSv1.2", r12


@case("profile_versions", kind="policy")
def t_versions(mod):
    ctx = _ctx(mod)
    for v in ("TLSv1", "TLSv1.1"):
        assert v in P["tls_versions"] or handshake_ok(ctx, client_context(v)) is None, "%s accepted" % v


@case("profile_ciphers", kind="policy")
def t_ciphers(mod):
    extra = sorted(pre13_ciphers(_ctx(mod)) - set(P["openssl"]))
    assert not extra, "cipher suites outside the profile: %s" % extra
