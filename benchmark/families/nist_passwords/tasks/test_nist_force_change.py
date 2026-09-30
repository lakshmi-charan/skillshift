import datetime

from sa_testlib import case, need

D = datetime.date


@case("functional")
def t_compromised(mod):
    f = need(mod, "must_change_password")
    assert f({"last_changed": D(2025, 1, 5), "compromised": True}, D(2025, 1, 6)) is True


@case("functional")
def t_recent(mod):
    f = need(mod, "must_change_password")
    assert f({"last_changed": D(2025, 1, 5), "compromised": False}, D(2025, 2, 6)) is False


@case("org_rules", states=["s0"])
def t_expiry_s0(mod):
    f = need(mod, "must_change_password")
    assert f({"last_changed": D(2019, 1, 1), "compromised": False}, D(2020, 1, 1)) is True


@case("prohibited_rules", kind="policy", states=["s1"])
def t_no_periodic(mod):
    f = need(mod, "must_change_password")
    assert f({"last_changed": D(2023, 1, 1), "compromised": False}, D(2025, 9, 1)) is False, "periodic change forced"
