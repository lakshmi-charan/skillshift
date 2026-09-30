import json

import numpy as np
import pandas as pd

from sa_testlib import case, need

ARR = '[{"id": 1, "name": "ada", "score": 9.5}, {"id": 2, "name": "bob", "score": 7.0}, {"id": 3, "name": "cy", "score": null}]'


@case("records_to_frame")
def h_records(mod):
    df = need(mod, "records_to_frame")(ARR)
    assert list(df.columns) == ["id", "name", "score"] and len(df) == 3
    assert df["id"].tolist() == [1, 2, 3] and df["name"].tolist() == ["ada", "bob", "cy"]
    assert df["score"].iloc[0] == 9.5 and pd.isna(df["score"].iloc[2])


@case("records_to_frame")
def h_records_single(mod):
    df = need(mod, "records_to_frame")('[{"sku": "X-1", "qty": 4}]')
    assert df.to_dict("records") == [{"sku": "X-1", "qty": 4}]


@case("records_to_frame")
def h_records_generated(mod):
    text = json.dumps([{"k": i, "v": i * 1.5} for i in range(50)])
    df = need(mod, "records_to_frame")(text)
    assert len(df) == 50 and float(df["v"].sum()) == sum(i * 1.5 for i in range(50))


@case("lines_to_frame")
def h_lines(mod):
    text = '{"id": 1, "tag": "a"}\n{"id": 2, "tag": "b"}\n{"id": 3, "tag": "c"}\n'
    df = need(mod, "lines_to_frame")(text)
    assert df["id"].tolist() == [1, 2, 3] and df["tag"].tolist() == ["a", "b", "c"]


@case("lines_to_frame")
def h_lines_missing_key(mod):
    df = need(mod, "lines_to_frame")('{"a": 1, "b": 2}\n{"a": 3}\n')
    assert df["a"].tolist() == [1, 3] and pd.isna(df["b"].iloc[1])


@case("frame_to_records")
def h_to_json(mod):
    df = pd.DataFrame({"id": [1, 2], "name": ["x", "y"], "score": [1.5, np.nan]})
    out = need(mod, "frame_to_records")(df)
    assert json.loads(out) == [{"id": 1, "name": "x", "score": 1.5}, {"id": 2, "name": "y", "score": None}]


@case("frame_to_records")
def h_to_json_empty(mod):
    assert json.loads(need(mod, "frame_to_records")(pd.DataFrame({"a": []}))) == []


@case("flatten_nested")
def h_flatten(mod):
    text = '[{"id": 1, "user": {"name": "ada", "geo": {"cc": "FR"}}}, {"id": 2, "user": {"name": "bob"}}]'
    df = need(mod, "flatten_nested")(text)
    assert set(df.columns) == {"id", "user.name", "user.geo.cc"}
    assert df["user.name"].tolist() == ["ada", "bob"] and pd.isna(df["user.geo.cc"].iloc[1])


@case("flatten_nested")
def h_flatten_flat(mod):
    df = need(mod, "flatten_nested")('[{"a": 1}, {"a": 2}]')
    assert df["a"].tolist() == [1, 2]
