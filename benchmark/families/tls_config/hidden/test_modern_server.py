import os
import ssl
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _policy import profile  # noqa: E402
from _tlsutil import CERT, KEY, client_context, handshake_ok, make_server  # noqa: E402
from sa_testlib import case, need, STATE  # noqa: E402

P = profile(STATE, "modern")


def _ctx(mod):
    return make_server(need(mod, "make_modern_server_context"), CERT, KEY)


@case("protocol_versions")
def h_profile_versions(mod):
    ctx = _ctx(mod)
    for v in P["tls_versions"]:
        r = handshake_ok(ctx, client_context(v))
        assert r is not None and r[0] == v, "%s client could not connect" % v


@case("protocol_versions")
def h_older_refused(mod):
    ctx = _ctx(mod)
    for v in ("TLSv1", "TLSv1.1", "TLSv1.2", "TLSv1.3"):
        if v not in P["tls_versions"]:
            assert handshake_ok(ctx, client_context(v)) is None, "%s handshake accepted" % v


@case("protocol_versions")
def h_tls13_suites(mod):
    ctx = _ctx(mod)
    for suite in P["ciphersuites"]:
        assert suite in {c["name"] for c in ctx.get_ciphers()}, suite


@case("client_cipher_order")
def h_no_server_preference(mod):
    ctx = _ctx(mod)
    if not P["server_preferred_order"]:
        assert not (ctx.options & ssl.OP_CIPHER_SERVER_PREFERENCE), "server cipher preference enforced"
