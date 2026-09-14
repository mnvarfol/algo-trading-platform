import asyncio
import logging
import signal
from datetime import datetime

from alor.client.config import Config
from alor.client.http.read import ReadClient
from alor.client.http.transport import HttpTransport
from alor.token.service import TokenService
from scheduling.loops import MOSCOW_TZ, run_daily_at, run_interval
from storage.postgres import PostgresConnection
from storage.redis import RedisConnection

from portfolios.refresher import PortfolioRefresher
from portfolios.repository import PortfolioRepository

logger = logging.getLogger(__name__)

PORTFOLIO_VALUE_REFRESH_INTERVAL = 15 * 60
RISK_CATEGORY_REFRESH_HOUR = 7
RISK_CATEGORY_REFRESH_MINUTE = 0


async def _close_all(*connections) -> None:
    for connection in connections:
        try:
            await connection.close()
        except Exception:
            logger.exception("Failed to close %s", connection)


async def main() -> None:
    logging.Formatter.converter = staticmethod(
        lambda secs: datetime.fromtimestamp(secs, tz=MOSCOW_TZ).timetuple()
    )
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s MSK %(levelname)s %(name)s: %(message)s",
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
            run_interval(
                "Portfolio value refresh",
                refresher.refresh_portfolio_values,
                PORTFOLIO_VALUE_REFRESH_INTERVAL,
                stop_event,
            ),
            run_daily_at(
                "Risk category refresh",
                refresher.refresh_risk_category_ids,
                RISK_CATEGORY_REFRESH_HOUR,
                RISK_CATEGORY_REFRESH_MINUTE,
                stop_event,
            ),
        )
    finally:
        await _close_all(transport, redis, postgres)


if __name__ == "__main__":
    asyncio.run(main())
