import asyncio
import time

from sa_testlib import case, need


async def _val(v, delay):
    await asyncio.sleep(delay)
    return v


@case("functional")
def t_all_fast(mod):
    f = need(mod, "run_with_deadline")
    assert f([_val(1, 0.01), _val(2, 0), _val(3, 0.02)], 1.0) == [1, 2, 3]


@case("functional")
def t_some_slow(mod):
    f = need(mod, "run_with_deadline")
    t0 = time.time()
    assert f([_val("a", 0.0), _val("b", 5), _val("c", 0.01)], 0.2) == ["a", None, "c"]
    assert time.time() - t0 < 3


@case("functional")
def t_repeated(mod):
    f = need(mod, "run_with_deadline")
    for i in range(3):
        assert f([_val(i, 0)], 0.5) == [i]
