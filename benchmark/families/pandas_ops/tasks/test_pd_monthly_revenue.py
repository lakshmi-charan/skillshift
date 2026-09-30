import json

from sa_testlib import case, need


@case("functional")
def t_basic(mod):
    f = need(mod, "monthly_revenue")
    text = json.dumps([{"date": "2023-01-05", "amount": 10}, {"date": "2023-01-30", "amount": 2.5},
                       {"date": "2023-03-01", "amount": 4}])
    out = f(text)
    assert out == {"2023-01": 12.5, "2023-02": 0.0, "2023-03": 4.0}
    assert list(out) == ["2023-01", "2023-02", "2023-03"]


@case("functional")
def t_unsorted_year_boundary(mod):
    f = need(mod, "monthly_revenue")
    text = json.dumps([{"date": "2024-01-31", "amount": 1.0}, {"date": "2023-11-15", "amount": 3.0},
                       {"date": "2023-11-01", "amount": 2.0}])
    assert f(text) == {"2023-11": 5.0, "2023-12": 0.0, "2024-01": 1.0}


@case("functional")
def t_single(mod):
    assert need(mod, "monthly_revenue")('[{"date": "2022-02-28", "amount": 7}]') == {"2022-02": 7.0}
