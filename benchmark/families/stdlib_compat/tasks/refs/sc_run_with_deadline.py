import asyncio


def run_with_deadline(coros, seconds):
    async def _one(c):
        try:
            return await asyncio.wait_for(c, seconds)
        except asyncio.TimeoutError:
            return None

    async def _main():
        return await asyncio.gather(*(_one(c) for c in coros))

    return asyncio.run(_main())
