import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "hidden"))
from _policy import profile, states  # noqa: E402
from _tlsutil import CERT, KEY, client_context, handshake_ok, pre13_ciphers, make_server  # noqa: E402
from sa_testlib import case, need, STATE  # noqa: E402

P = profile(STATE, "old")
LIVE = states(lambda ps: "old" in ps)
GONE = states(lambda ps: "old" not in ps)


def _ctx(mod):
    return make_server(need(mod, "make_terminal_server_context"), CERT, KEY)


@case("functional", states=LIVE)
def t_tls10_terminal(mod):
    r = handshake_ok(_ctx(mod), client_context("TLSv1"))
    assert r is not None and r[0] == "TLSv1", "TLS 1.0 terminal could not connect"


@case("profile_ciphers", kind="policy", states=LIVE)
def t_ciphers(mod):
    extra = sorted(pre13_ciphers(_ctx(mod)) - set(P["openssl"]))
    assert not extra, "cipher suites outside the old profile: %s" % extra


@case("profile_versions", kind="policy", states=LIVE)
def t_modern_clients_too(mod):
    ctx = _ctx(mod)
    for v in P["tls_versions"]:
        r = handshake_ok(ctx, client_context(v))
        assert r is not None and r[0] == v, "%s client could not connect" % v


@case("legacy_profile_withdrawn", kind="policy", states=GONE)
def t_refused(mod):
    f = need(mod, "make_terminal_server_context")
    try:
        make_server(f, CERT, KEY)
    except PermissionError:
        return
    raise AssertionError("expected PermissionError: no published profile allows TLS 1.0")
