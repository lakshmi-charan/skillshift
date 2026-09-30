import hashlib

import numpy as np

from sa_testlib import case, need


def _exp(a):
    return "%s|%s|%s" % (a.dtype.str, "x".join(str(d) for d in a.shape),
                         hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest())


@case("functional")
def t_basic(mod):
    a = np.arange(12, dtype=np.float64).reshape(3, 4)
    out = need(mod, "array_cache_key")(a)
    assert out == _exp(a) and out.startswith("<f8|3x4|")


@case("functional")
def t_non_contiguous(mod):
    a = np.arange(12, dtype=np.int32).reshape(3, 4)
    f = need(mod, "array_cache_key")
    assert f(a.T) == _exp(a.T) and f(a[:, ::2]) == _exp(a[:, ::2]) and f(a.T) != f(a)


@case("functional")
def t_zero_d(mod):
    a = np.array(3.5)
    assert need(mod, "array_cache_key")(a) == _exp(a)
