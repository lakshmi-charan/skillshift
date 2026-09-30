import numpy as np

from sa_testlib import case, need


@case("to_bytes")
def test_bytes(mod):
    a = np.array([1, 2, 3], dtype=np.int32)
    assert need(mod, "to_bytes")(a) == a.tostring()


@case("from_bytes")
def test_roundtrip(mod):
    a = np.array([1.5, 2.5])
    assert need(mod, "from_bytes")(need(mod, "to_bytes")(a)).tolist() == [1.5, 2.5]


@case("npy_bytes")
def test_npy(mod):
    a = np.eye(2)
    assert (need(mod, "load_npy")(need(mod, "dump_npy")(a)) == a).all()
