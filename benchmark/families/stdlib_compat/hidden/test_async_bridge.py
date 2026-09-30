import asyncio
import time

from sa_testlib import case, need


def _drive(coro):
    """Run an awaitable on a private loop (does not touch the thread's current event loop)."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


async def _add(a, b, delay=0):
    await asyncio.sleep(delay)
    return a + b


async def _boom():
    await asyncio.sleep(0)
    raise ValueError("boom")


@case("run_sync")
def h_run_sync(mod):
    f = need(mod, "run_sync")
    assert f(_add(2, 3)) == 5
    assert f(_add("a", "b", 0.01)) == "ab"


@case("run_sync")
def h_run_sync_error(mod):
    f = need(mod, "run_sync")
    try:
        f(_boom())
    except ValueError:
        pass
    else:
        raise AssertionError("exception not propagated")
    assert f(_add(1, 1)) == 2


@case("run_all")
def h_run_all_order(mod):
    f = need(mod, "run_all")
    out = f([_add(1, 0, 0.03), _add(2, 0, 0.0), _add(3, 0, 0.01)])
    assert out == [1, 2, 3]


@case("run_all")
def h_run_all_limit(mod):
    f = need(mod, "run_all")
    state = {"now": 0, "max": 0}

    async def job(i):
        state["now"] += 1
        state["max"] = max(state["max"], state["now"])
        await asyncio.sleep(0.01)
        state["now"] -= 1
        return i * i

    assert f([job(i) for i in range(8)], limit=2) == [i * i for i in range(8)]
    assert state["max"] == 2
    state["max"] = 0
    assert f([job(i) for i in range(5)]) == [0, 1, 4, 9, 16]
    assert state["max"] == 5


@case("with_timeout")
def h_timeout(mod):
    f = need(mod, "with_timeout")
    t0 = time.time()
    assert _drive(f(asyncio.sleep(5, result="late"), 0.05)) is None
    assert time.time() - t0 < 2
    assert _drive(f(asyncio.sleep(5), 0.02, default="fallback")) == "fallback"


@case("with_timeout")
def h_timeout_fast(mod):
    f = need(mod, "with_timeout")
    assert _drive(f(_add(4, 5), 1.0)) == 9


@case("retry_async")
def h_retry_success(mod):
    f = need(mod, "retry_async")
    calls = []

    async def flaky():
        calls.append(1)
        if len(calls) < 3:
            raise ConnectionError("try again")
        return "ok"

    assert _drive(f(flaky, attempts=3)) == "ok" and len(calls) == 3


@case("retry_async")
def h_retry_exhausted(mod):
    f = need(mod, "retry_async")
    calls = []

    async def bad():
        calls.append(1)
        raise ConnectionError("down %d" % len(calls))

    try:
        _drive(f(bad, attempts=2))
    except ConnectionError as e:
        assert str(e) == "down 2" and len(calls) == 2
    else:
        raise AssertionError("expected ConnectionError")


@case("retry_async")
def h_retry_other_exception(mod):
    f = need(mod, "retry_async")
    calls = []

    async def wrong():
        calls.append(1)
        raise KeyError("x")

    try:
        _drive(f(wrong, attempts=5, exceptions=(ConnectionError,)))
    except KeyError:
        assert len(calls) == 1
    else:
        raise AssertionError("expected KeyError")
