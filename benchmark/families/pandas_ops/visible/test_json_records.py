import pandas as pd

from sa_testlib import case, need


@case("records_to_frame")
def test_records(mod):
    df = need(mod, "records_to_frame")('[{"a": 1, "b": "x"}, {"a": 2, "b": "y"}]')
    assert df["a"].tolist() == [1, 2] and df["b"].dtype == object


@case("lines_to_frame")
def test_lines(mod):
    assert need(mod, "lines_to_frame")('{"a": 1}\n{"a": 2}\n')["a"].tolist() == [1, 2]


@case("frame_to_records")
def test_to_json(mod):
    assert need(mod, "frame_to_records")(pd.DataFrame({"a": [1]})) == '[{"a":1}]'
