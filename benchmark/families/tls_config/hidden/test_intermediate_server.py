import os
import ssl
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _policy import profile  # noqa: E402
from _tlsutil import CERT, KEY, client_context, handshake_ok, pre13_ciphers, make_server  # noqa: E402
from sa_testlib import case, need, STATE  # noqa: E402

P = profile(STATE, "intermediate")


def _ctx(mod):
    return make_server(need(mod, "make_intermediate_server_context"), CERT, KEY)


@case("protocol_versions")
def h_versions_in_profile(mod):
    ctx = _ctx(mod)
    for v in P["tls_versions"]:
        r = handshake_ok(ctx, client_context(v))
        assert r is not None and r[0] == v, "%s client could not connect" % v


@case("protocol_versions")
def h_versions_outside_profile(mod):
    ctx = _ctx(mod)
    for v in ("TLSv1", "TLSv1.1", "TLSv1.2", "TLSv1.3"):
        if v not in P["tls_versions"]:
            assert handshake_ok(ctx, client_context(v)) is None, "%s handshake accepted" % v


@case("protocol_versions")
def h_default_client(mod):
    r = handshake_ok(_ctx(mod), client_context())
    assert r is not None and r[0] == "TLSv1.3"


@case("cipher_allowlist", kind="policy")
def h_enabled_subset(mod):
    extra = sorted(pre13_ciphers(_ctx(mod)) - set(P["openssl"]))
    assert not extra, "cipher suites outside the intermediate profile enabled: %s" % extra


@case("cipher_allowlist", kind="policy")
def h_cbc_client_refused(mod):
    cbc = "ECDHE-RSA-AES128-SHA256:ECDHE-RSA-AES128-SHA:AES128-GCM-SHA256:AES128-SHA"
    assert handshake_ok(_ctx(mod), client_context("TLSv1.2", cbc)) is None, "non-profile suite negotiated"


@case("ecdhe_suites")
def h_ecdhe_present(mod):
    want = {c for c in P["openssl"] if c.startswith("ECDHE-")}
    missing = sorted(want - pre13_ciphers(_ctx(mod)))
    assert not missing, "profile ECDHE suites not enabled: %s" % missing


@case("ecdhe_suites")
def h_ecdhe_negotiated(mod):
    ctx = _ctx(mod)
    for c in ("ECDHE-RSA-AES128-GCM-SHA256", "ECDHE-RSA-CHACHA20-POLY1305", "ECDHE-RSA-AES256-GCM-SHA384"):
        r = handshake_ok(ctx, client_context("TLSv1.2", c))
        assert r == ("TLSv1.2", c), "TLS 1.2 client offering only %s: %r" % (c, r)


@case("ecdhe_suites")
def h_tls13_suites(mod):
    names = {c["name"] for c in _ctx(mod).get_ciphers() if c.get("protocol") == "TLSv1.3"}
    assert set(P["ciphersuites"]) <= names, names


@case("client_cipher_order")
def h_no_server_preference(mod):
    ctx = _ctx(mod)
    if not P["server_preferred_order"]:
        assert not (ctx.options & ssl.OP_CIPHER_SERVER_PREFERENCE), "server cipher preference enforced"


@case("client_cipher_order")
def h_client_choice_wins(mod):
    ctx = _ctx(mod)
    for order in ("ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-GCM-SHA256",
                  "ECDHE-RSA-CHACHA20-POLY1305:ECDHE-RSA-AES128-GCM-SHA256"):
        r = handshake_ok(ctx, client_context("TLSv1.2", order))
        assert r is not None and r[1] == order.split(":")[0], "client preference ignored: %r" % (r,)
