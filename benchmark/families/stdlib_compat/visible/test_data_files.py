import os
import tempfile

from sa_testlib import case, need


@case("json_files")
def test_json(mod):
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "x.json")
        need(mod, "write_json_atomic")(p, {"a": 1})
        assert need(mod, "read_json")(p) == {"a": 1}


@case("csv_files")
def test_csv(mod):
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "x.csv")
        need(mod, "write_csv_records")(p, [{"a": 1}])
        assert need(mod, "read_csv_records")(p) == [{"a": "1"}]
