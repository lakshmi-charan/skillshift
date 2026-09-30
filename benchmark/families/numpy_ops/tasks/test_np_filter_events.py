import numpy as np

from sa_testlib import case, need


@case("functional")
def t_basic(mod):
    f = need(mod, "filter_events")
    assert f([4, 1, 2, 4, 3, 5], [1, 2, 3, 4], [3]) == [4, 1, 2, 4]


@case("functional")
def t_arrays_and_empty(mod):
    f = need(mod, "filter_events")
    assert f(np.array([7, 8, 9]), np.array([10]), np.array([], dtype=int)) == []
    assert f([], [1], [2]) == []


@case("functional")
def t_large(mod):
    f = need(mod, "filter_events")
    ids = list(range(20000)) * 2
    out = f(ids, list(range(0, 20000, 2)), list(range(0, 20000, 3)))
    exp = [i for i in ids if i % 2 == 0 and i % 3 != 0]
    assert out == exp and all(isinstance(v, int) for v in out[:5])
