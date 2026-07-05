from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from .balance_topups import BalanceTopupsRepository
from .base import BaseRepository
from .checks import ChecksRepository
from .stars_orders import StarsOrdersRepository
from .stars_sell_orders import StarsSellOrdersRepository
from .users import UsersRepository


class Repository(BaseRepository):
    balance_topups: BalanceTopupsRepository
    checks: ChecksRepository
    stars_orders: StarsOrdersRepository
    stars_sell_orders: StarsSellOrdersRepository
    users: UsersRepository

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session=session)
        self.balance_topups = BalanceTopupsRepository(session=session)
        self.checks = ChecksRepository(session=session)
        self.stars_orders = StarsOrdersRepository(session=session)
        self.stars_sell_orders = StarsSellOrdersRepository(session=session)
        self.users = UsersRepository(session=session)
