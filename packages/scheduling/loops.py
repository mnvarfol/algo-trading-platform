import asyncio
import logging
from collections.abc import Awaitable, Callable
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)

MOSCOW_TZ = ZoneInfo("Europe/Moscow")


async def run_interval(
    name: str,
    fn: Callable[[], Awaitable[None]],
    interval: float,
    stop_event: asyncio.Event,
) -> None:
    while not stop_event.is_set():
        try:
            await fn()
        except Exception:
            logger.exception("%s cycle failed", name)
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=interval)
        except TimeoutError:
            pass


def seconds_until(hour: int, minute: int) -> float:
    now = datetime.now(MOSCOW_TZ)
    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if target <= now:
        target += timedelta(days=1)
    return (target - now).total_seconds()


async def run_daily_at(
    name: str,
    fn: Callable[[], Awaitable[None]],
    hour: int,
    minute: int,
    stop_event: asyncio.Event,
) -> None:
    while not stop_event.is_set():
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=seconds_until(hour, minute))
            break
        except TimeoutError:
            pass
        try:
            await fn()
        except Exception:
            logger.exception("%s cycle failed", name)
