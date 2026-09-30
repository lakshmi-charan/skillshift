import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _policy import profiles  # noqa: E402
from sa_testlib import case, need, STATE  # noqa: E402

MIN_AGE = max(p["hsts_min_age"] for p in profiles(STATE).values())


def _directives(value):
    out = {}
    for part in value.split(";"):
        part = part.strip()
        if part:
            k, _, v = part.partition("=")
            out[k.strip().lower()] = v.strip().strip('"')
    return out


@case("max_age", kind="policy")
def h_max_age(mod):
    f = need(mod, "hsts_header")
    for args in ((), (False,), (True, True)):
        d = _directives(f(*args))
        assert int(d["max-age"]) >= MIN_AGE, "max-age %s < %d" % (d.get("max-age"), MIN_AGE)


@case("directives")
def h_subdomains(mod):
    f = need(mod, "hsts_header")
    assert "includesubdomains" in _directives(f(True)) and "includesubdomains" in _directives(f())
    assert "includesubdomains" not in _directives(f(False))


@case("directives")
def h_preload(mod):
    f = need(mod, "hsts_header")
    assert "preload" in _directives(f(True, True))
    assert "preload" not in _directives(f(True, False)) and "preload" not in _directives(f())
