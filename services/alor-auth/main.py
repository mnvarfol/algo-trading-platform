import asyncio
import logging
import os

from alor.client.config import Config
from alor.client.http.auth import AuthClient
from alor.client.http.transport import HttpTransport
from refresher import TokenRefresher
from repository import AccountRepository
from storage.postgres import PostgresConnection
from storage.redis import RedisConnection

logger = logging.getLogger(__name__)

REFRESH_INTERVAL = 15 * 60


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    postgres = PostgresConnection(
        host=os.environ["POSTGRES_HOST"],
        port=int(os.environ["POSTGRES_PORT"]),
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        database=os.environ["POSTGRES_DB"],
    )
    redis = RedisConnection(
        host=os.environ["REDIS_HOST"],
        port=int(os.environ["REDIS_PORT"]),
        password=os.environ["REDIS_PASSWORD"],
    )
    transport = HttpTransport()

    await postgres.init()
    await redis.init()
    await transport.init()

    try:
        repository = AccountRepository(postgres)
        auth_client = AuthClient(transport, Config())
        refresher = TokenRefresher(repository, auth_client, redis, os.environ["ENCRYPTION_KEY"])

        while True:
            try:
                await refresher.refresh_all()
            except Exception:
                logger.exception("Token refresh cycle failed")
            await asyncio.sleep(REFRESH_INTERVAL)
    finally:
        await transport.close()
        await redis.close()
        await postgres.close()


if __name__ == "__main__":
    asyncio.run(main())
