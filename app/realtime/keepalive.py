"""Self-ping keep-alive so Render's free tier doesn't sleep the service."""
import asyncio
import logging

log = logging.getLogger("keepalive")


async def _loop(url: str, interval: int):
    # lazy import so the app runs even if httpx isn't installed locally
    import httpx
    await asyncio.sleep(interval)  # wait one interval before first ping
    async with httpx.AsyncClient(timeout=10) as client:
        while True:
            try:
                r = await client.get(url)
                log.info("keep-alive ping %s -> %s", url, r.status_code)
            except Exception as e:  # noqa: BLE001
                log.warning("keep-alive ping failed: %s", e)
            await asyncio.sleep(interval)


def start_keepalive(url: str, interval: int) -> asyncio.Task | None:
    if not url:
        return None
    return asyncio.create_task(_loop(url, interval))
