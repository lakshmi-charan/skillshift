import datetime

from sa_testlib import case, need, getfn

D = datetime.date


@case("compromise")
def h_compromised(mod):
    f = need(mod, "password_change_required")
    assert f(D(2025, 9, 1), D(2025, 9, 2), compromised=True) is True


@case("compromise")
def h_fresh_ok(mod):
    f = need(mod, "password_change_required")
    assert f(D(2025, 9, 1), D(2025, 9, 30), compromised=False) is False


@case("periodic_expiry", states=["s0"])
def h_expiry(mod):
    f = need(mod, "password_change_required")
    assert f(D(2019, 1, 1), D(2020, 1, 1), compromised=False) is True      # 365 days
    assert f(D(2019, 1, 2), D(2020, 1, 1), compromised=False) is False     # 364 days


@case("periodic_expiry", kind="obsolete", states=["s1"])
def o_expiry(mod):
    f = getfn(mod, "password_change_required")
    if f is None:
        return
    for days in (365, 400, 2000):
        assert f(D(2020, 1, 1), D(2020, 1, 1) + datetime.timedelta(days=days), compromised=False) is False, \
            "periodic change required after %d days" % days
