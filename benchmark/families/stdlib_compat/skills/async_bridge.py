"""Call asyncio code from synchronous code (CLI commands, WSGI views, scripts)."""
import asyncio


def run_sync(coro):
    """Run a coroutine to completion from synchronous code and return its result."""
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro)


def run_all(coros, limit=None):
    """Run coroutines concurrently (at most `limit` at a time) and return their results in order."""
    async def _main():
        sem = asyncio.Semaphore(limit) if limit else None

        async def _one(c):
            if sem is None:
                return await c
            async with sem:
                return await c

        return await asyncio.gather(*(_one(c) for c in coros))

    return run_sync(_main())


async def with_timeout(coro, seconds, default=None):
    """Await `coro`; return `default` if it does not finish within `seconds`."""
    try:
        return await asyncio.wait_for(coro, seconds)
    except asyncio.TimeoutError:
        return default


async def retry_async(func, attempts=3, delay=0.0, exceptions=(Exception,)):
    """Await func() until it succeeds, at most `attempts` times; re-raise the last error."""
    for i in range(attempts):
        try:
            return await func()
        except exceptions:
            if i == attempts - 1:
                raise
            await asyncio.sleep(delay)
