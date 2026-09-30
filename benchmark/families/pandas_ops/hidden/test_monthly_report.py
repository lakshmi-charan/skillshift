import pandas as pd

from sa_testlib import case, need

DF = pd.DataFrame({
    "date": ["2023-01-03", "2023-01-20", "2023-03-15", "2023-04-01", "2023-12-31", "2024-02-29"],
    "amount": [10.0, 5.0, 2.5, 1.0, 4.0, 8.0],
})


def _pairs(s):
    return [(str(pd.Timestamp(i).date()), float(v)) for i, v in s.items()]


@case("monthly_totals")
def h_monthly(mod):
    out = need(mod, "monthly_totals")(DF.iloc[:4])
    assert _pairs(out) == [("2023-01-31", 15.0), ("2023-02-28", 0.0), ("2023-03-31", 2.5), ("2023-04-30", 1.0)]


@case("monthly_totals")
def h_monthly_leap_and_cols(mod):
    df = DF.rename(columns={"date": "when", "amount": "v"}).iloc[4:]
    out = need(mod, "monthly_totals")(df, date_col="when", value_col="v")
    p = _pairs(out)
    assert p[0] == ("2023-12-31", 4.0) and p[-1] == ("2024-02-29", 8.0) and len(p) == 3


@case("monthly_totals")
def h_monthly_unsorted(mod):
    out = need(mod, "monthly_totals")(DF.iloc[[3, 0, 2, 1]])
    assert _pairs(out)[0] == ("2023-01-31", 15.0) and len(out) == 4


@case("quarterly_totals")
def h_quarterly(mod):
    out = need(mod, "quarterly_totals")(DF)
    p = _pairs(out)
    assert p[:2] == [("2023-03-31", 17.5), ("2023-06-30", 1.0)]
    assert p[-1] == ("2024-03-31", 8.0) and len(p) == 5


@case("quarterly_totals")
def h_quarterly_single(mod):
    assert _pairs(need(mod, "quarterly_totals")(DF.iloc[:2])) == [("2023-03-31", 15.0)]


@case("yearly_totals")
def h_yearly(mod):
    assert _pairs(need(mod, "yearly_totals")(DF)) == [("2023-12-31", 22.5), ("2024-12-31", 8.0)]


@case("yearly_totals")
def h_yearly_gap(mod):
    df = pd.DataFrame({"date": ["2020-06-01", "2022-06-01"], "amount": [1.0, 2.0]})
    assert _pairs(need(mod, "yearly_totals")(df)) == [("2020-12-31", 1.0), ("2021-12-31", 0.0), ("2022-12-31", 2.0)]


@case("daily_average")
def h_daily(mod):
    df = pd.DataFrame({"date": ["2023-01-01", "2023-01-01", "2023-01-03"], "amount": [1.0, 3.0, 5.0]})
    assert _pairs(need(mod, "daily_average")(df)) == [("2023-01-01", 2.0), ("2023-01-03", 5.0)]


@case("daily_average")
def h_daily_timestamps(mod):
    df = pd.DataFrame({"date": ["2023-01-01 08:00", "2023-01-01 20:00"], "amount": [2.0, 4.0]})
    assert _pairs(need(mod, "daily_average")(df)) == [("2023-01-01", 3.0)]


@case("month_label_totals")
def h_labels(mod):
    out = need(mod, "month_label_totals")(DF)
    assert out == {"2023-01": 15.0, "2023-03": 2.5, "2023-04": 1.0, "2023-12": 4.0, "2024-02": 8.0}


@case("month_label_totals")
def h_labels_cols(mod):
    df = pd.DataFrame({"d": ["2021-07-31", "2021-08-01"], "x": [1, 2]})
    assert need(mod, "month_label_totals")(df, date_col="d", value_col="x") == {"2021-07": 1.0, "2021-08": 2.0}
