import asyncio
import logging
import os
import signal
import time

from alor.client.config import Config
from alor.client.http.auth import AuthClient
from alor.client.http.transport import HttpTransport
from storage.postgres import PostgresConnection
from storage.redis import RedisConnection

from auth.refresher import TokenRefresher
from auth.repository import AccountRepository

logger = logging.getLogger(__name__)

REFRESH_INTERVAL = 15 * 60


async def _close_all(*connections) -> None:
    for connection in connections:
        try:
            await connection.close()
        except Exception:
            logger.exception("Failed to close %s", connection)


async def main() -> None:
    logging.Formatter.converter = time.gmtime
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s UTC %(levelname)s %(name)s: %(message)s",
    )

    postgres = PostgresConnection.from_env()
    redis = RedisConnection.from_env()
    transport = HttpTransport()

    try:
        await postgres.init()
        await redis.init()
        await transport.init()
    except Exception:
        await _close_all(postgres, redis, transport)
        raise

    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()
    try:
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(sig, stop_event.set)
    except NotImplementedError:
        # add_signal_handler isn't supported on Windows; SIGINT still
        # raises KeyboardInterrupt there, just without a graceful stop_event.
        pass

    try:
        repository = AccountRepository(postgres)
        auth_client = AuthClient(transport, Config())
        refresher = TokenRefresher(repository, auth_client, redis, os.environ["ENCRYPTION_KEY"])

        while not stop_event.is_set():
            try:
                await refresher.refresh_all()
            except Exception:
                logger.exception("Token refresh cycle failed")
            try:
                await asyncio.wait_for(stop_event.wait(), timeout=REFRESH_INTERVAL)
            except TimeoutError:
                pass
    finally:
        await _close_all(transport, redis, postgres)


if __name__ == "__main__":
    asyncio.run(main())
