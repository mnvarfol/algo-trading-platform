import asyncio
import logging
from decimal import Decimal

from alor.client.http.read import ReadClient
from alor.token.service import TokenService

from portfolios.models import Portfolio
from portfolios.repository import PortfolioRepository

logger = logging.getLogger(__name__)


class PortfolioRefresher:

    def __init__(
        self,
        portfolio_repository: PortfolioRepository,
        token_service: TokenService,
        read_client: ReadClient,
    ):
        self._portfolio_repository = portfolio_repository
        self._token_service = token_service
        self._read_client = read_client

    async def refresh_portfolio_values(self) -> None:
        portfolios = await self._portfolio_repository.get_active()
        results = await asyncio.gather(
            *(self._refresh_portfolio_value(portfolio) for portfolio in portfolios),
            return_exceptions=True,
        )
        for portfolio, result in zip(portfolios, results, strict=True):
            if isinstance(result, BaseException):
                logger.error(
                    "Failed to refresh portfolio_value for portfolio %s:%s:%s",
                    portfolio.account_id,
                    portfolio.portfolio,
                    portfolio.exchange,
                    exc_info=result,
                )

    async def _refresh_portfolio_value(self, portfolio: Portfolio) -> None:
        access_token = await self._token_service.get_access_token(portfolio.account_id)
        if not access_token:
            raise RuntimeError(f"No access token for account {portfolio.account_id}")

        data = await self._read_client.get_portfolio_summary(
            access_token,
            portfolio.exchange,
            portfolio.portfolio,
        )
        portfolio_value = Decimal(str(data["plv"]))

        await self._portfolio_repository.update_portfolio_value(
            portfolio.id,
            portfolio_value,
        )

    async def refresh_risk_category_ids(self) -> None:
        portfolios = await self._portfolio_repository.get_active()
        results = await asyncio.gather(
            *(self._refresh_risk_category_id(portfolio) for portfolio in portfolios),
            return_exceptions=True,
        )
        for portfolio, result in zip(portfolios, results, strict=True):
            if isinstance(result, BaseException):
                logger.error(
                    "Failed to refresh risk_category_id for portfolio %s:%s:%s",
                    portfolio.account_id,
                    portfolio.portfolio,
                    portfolio.exchange,
                    exc_info=result,
                )

    async def _refresh_risk_category_id(self, portfolio: Portfolio) -> None:
        access_token = await self._token_service.get_access_token(portfolio.account_id)
        if not access_token:
            raise RuntimeError(f"No access token for account {portfolio.account_id}")

        data = await self._read_client.get_portfolio_risk(
            access_token,
            portfolio.exchange,
            portfolio.portfolio,
        )
        risk_category_id = data["rid"]

        await self._portfolio_repository.update_risk_category_id(
            portfolio.id,
            risk_category_id,
        )
