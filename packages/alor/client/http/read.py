from alor.client.config import Config
from alor.client.http.transport import HttpTransport


class ReadClient:

    def __init__(
        self,
        transport: HttpTransport,
        config: Config,
    ):
        self._transport = transport
        self._config = config

    async def get_portfolio_summary(
        self,
        access_token: str,
        exchange: str,
        portfolio: str,
    ) -> dict:
        url = f"{self._config.http_url}/md/v2/Clients/{exchange}/{portfolio}/summary"
        return await self._transport.get(
            url,
            headers={"Authorization": f"Bearer {access_token}"},
            params={"format": "Slim"},
        )

    async def get_portfolio_risk(
        self,
        access_token: str,
        exchange: str,
        portfolio: str,
    ) -> dict:
        url = f"{self._config.http_url}/md/v2/Clients/{exchange}/{portfolio}/risk"
        return await self._transport.get(
            url,
            headers={"Authorization": f"Bearer {access_token}"},
            params={"format": "Slim"},
        )