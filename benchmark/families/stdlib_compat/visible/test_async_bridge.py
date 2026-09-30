import asyncio

from sa_testlib import case, need


async def _double(x):
    await asyncio.sleep(0)
    return 2 * x


@case("run_sync")
def test_run_sync(mod):
    assert need(mod, "run_sync")(_double(21)) == 42


@case("run_all")
def test_run_all(mod):
    assert need(mod, "run_all")([_double(1), _double(2)]) == [2, 4]
