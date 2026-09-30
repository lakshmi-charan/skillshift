import pandas as pd

from sa_testlib import case, need

DF = pd.DataFrame({"date": ["2023-01-03", "2023-01-20", "2023-03-15"], "amount": [10.0, 5.0, 2.5]})


@case("monthly_totals")
def test_monthly(mod):
    out = need(mod, "monthly_totals")(DF)
    assert out.tolist() == [15.0, 0.0, 2.5]
    assert out.index.freqstr == "M"


@case("quarterly_totals")
def test_quarterly(mod):
    out = need(mod, "quarterly_totals")(DF)
    assert out.tolist() == [17.5] and out.index.freqstr == "Q-DEC"


@case("month_label_totals")
def test_labels(mod):
    assert need(mod, "month_label_totals")(DF) == {"2023-01": 15.0, "2023-03": 2.5}
