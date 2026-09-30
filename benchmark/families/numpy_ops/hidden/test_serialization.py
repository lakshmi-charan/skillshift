import hashlib

import numpy as np

from sa_testlib import case, need


@case("to_bytes")
def h_to_bytes(mod):
    a = np.array([1.0, 2.5, -3.0])
    out = need(mod, "to_bytes")(a)
    assert isinstance(out, bytes) and out == a.tobytes() and len(out) == 24


@case("to_bytes")
def h_to_bytes_c_order(mod):
    a = np.arange(6, dtype=np.int32).reshape(2, 3).T
    assert need(mod, "to_bytes")(a) == np.ascontiguousarray(a).tobytes()


@case("to_bytes")
def h_to_bytes_list(mod):
    assert need(mod, "to_bytes")([1, 2]) == np.array([1, 2]).tobytes()


@case("from_bytes")
def h_from_bytes(mod):
    f = need(mod, "from_bytes")
    a = np.array([1.0, 2.5, -3.0])
    out = f(a.tobytes())
    assert out.dtype == np.float64 and out.tolist() == [1.0, 2.5, -3.0]


@case("from_bytes")
def h_from_bytes_shape_dtype(mod):
    a = np.arange(12, dtype=np.int16).reshape(3, 4)
    out = need(mod, "from_bytes")(a.tobytes(), dtype="int16", shape=(3, 4))
    assert out.shape == (3, 4) and out.dtype == np.int16 and (out == a).all()


@case("digest")
def h_digest(mod):
    a = np.linspace(0, 1, 5)
    assert need(mod, "digest")(a) == hashlib.sha256(a.tobytes()).hexdigest()


@case("digest")
def h_digest_distinguishes(mod):
    f = need(mod, "digest")
    a = np.arange(6, dtype=np.int64).reshape(2, 3)
    assert f(a) == f(a.copy()) and f(a) != f(a + 1)
    assert f(a.T) == hashlib.sha256(np.ascontiguousarray(a.T).tobytes()).hexdigest()


@case("npy_bytes")
def h_npy(mod):
    a = np.arange(6, dtype=np.float32).reshape(2, 3)
    data = need(mod, "dump_npy")(a)
    assert isinstance(data, bytes) and data[:6] == b"\x93NUMPY"
    back = need(mod, "load_npy")(data)
    assert back.dtype == np.float32 and back.shape == (2, 3) and (back == a).all()


@case("npy_bytes")
def h_npy_scalar_bool(mod):
    a = np.array([True, False])
    assert need(mod, "load_npy")(need(mod, "dump_npy")(a)).tolist() == [True, False]
