import json
import os
import tempfile

from sa_testlib import case, need


@case("json_files")
def h_json_roundtrip(mod):
    r, w = need(mod, "read_json"), need(mod, "write_json_atomic")
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "state.json")
        data = {"b": [1, 2, {"c": None}], "a": "Zoë", "n": 1.5}
        w(p, data)
        assert r(p) == data
        text = open(p, encoding="utf-8").read()
        assert text == json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


@case("json_files")
def h_json_missing(mod):
    r = need(mod, "read_json")
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "nope.json")
        assert r(p) is None
        assert r(p, default={}) == {}


@case("atomic_write")
def h_atomic(mod):
    w = need(mod, "write_json_atomic")
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "cfg.json")
        w(p, {"v": 1})
        w(p, {"v": 2})
        assert json.load(open(p, encoding="utf-8")) == {"v": 2}
        assert os.listdir(d) == ["cfg.json"], os.listdir(d)


@case("atomic_write")
def h_atomic_failure_keeps_old(mod):
    w = need(mod, "write_json_atomic")
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "cfg.json")
        w(p, {"v": 1})
        try:
            w(p, {"bad": object()})
        except TypeError:
            pass
        assert json.load(open(p, encoding="utf-8")) == {"v": 1}
        assert os.listdir(d) == ["cfg.json"], os.listdir(d)


@case("csv_files")
def h_csv_roundtrip(mod):
    w, r = need(mod, "write_csv_records"), need(mod, "read_csv_records")
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "out.csv")
        rows = [{"name": "a, b", "qty": 3}, {"name": 'say "hi"', "qty": 4}]
        w(p, rows)
        assert r(p) == [{"name": "a, b", "qty": "3"}, {"name": 'say "hi"', "qty": "4"}]


@case("csv_files")
def h_csv_fieldnames(mod):
    w, r = need(mod, "write_csv_records"), need(mod, "read_csv_records")
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "out.csv")
        w(p, [{"x": 1, "y": 2}], fieldnames=["y", "x"])
        assert open(p, encoding="utf-8").read().splitlines()[0] == "y,x"
        assert r(p) == [{"y": "2", "x": "1"}]
