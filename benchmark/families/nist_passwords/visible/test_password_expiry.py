import datetime

from sa_testlib import case, need


@case("periodic_expiry")
def test_one_year(mod):
    assert need(mod, "password_change_required")(datetime.date(2019, 3, 1), datetime.date(2020, 3, 1)) is True


@case("compromise")
def test_compromised(mod):
    assert need(mod, "password_change_required")(datetime.date(2020, 3, 1), datetime.date(2020, 3, 2), True) is True
