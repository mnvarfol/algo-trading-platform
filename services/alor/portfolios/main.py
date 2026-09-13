import asyncio
import logging
import signal
import time

from alor.client.config import Config
from alor.client.http.read import ReadClient
from alor.client.http.transport import HttpTransport
from alor.token.service import TokenService
from storage.postgres import PostgresConnection
from storage.redis import RedisConnection

from portfolios.refresher import PortfolioRefresher
from portfolios.repository import PortfolioRepository

logger = logging.getLogger(__name__)

PORTFOLIO_VALUE_REFRESH_INTERVAL = 15 * 60
RISK_CATEGORY_REFRESH_INTERVAL = 24 * 60 * 60


async def _close_all(*connections) -> None:
    for connection in connections:
        try:
            await connection.close()
        except Exception:
            logger.exception("Failed to close %s", connection)


async def _run_loop(name: str, fn, interval: float, stop_event: asyncio.Event) -> None:
    while not stop_event.is_set():
        try:
            await fn()
        except Exception:
            logger.exception("%s cycle failed", name)
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=interval)
        except TimeoutError:
            pass


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
        pass

    try:
        portfolio_repository = PortfolioRepository(postgres)
        token_service = TokenService(redis)
        read_client = ReadClient(transport, Config())

        refresher = PortfolioRefresher(portfolio_repository, token_service, read_client)

        await asyncio.gather(
            _run_loop(
                "Portfolio value refresh",
                refresher.refresh_portfolio_values,
                PORTFOLIO_VALUE_REFRESH_INTERVAL,
                stop_event,
            ),
            _run_loop(
                "Risk category refresh",
                refresher.refresh_risk_category_ids,
                RISK_CATEGORY_REFRESH_INTERVAL,
                stop_event,
            ),
        )
    finally:
        await _close_all(transport, redis, postgres)


if __name__ == "__main__":
    asyncio.run(main())
