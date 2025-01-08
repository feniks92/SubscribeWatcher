from sqlalchemy import and_, select

from libs.database.models import GigaTariff, PaymentSystem
from libs.database import tables as db

from .base import Base


class DictDatasource(Base):
    async def get_all(self, active_only=True):
        query = select(self.table)
        if active_only:
            query = query.where(self.table.active.is_(active_only))

        return self._get_list(query)


class GigaTariffDatasource(DictDatasource):
    table = db.GigaTariff
    model = GigaTariff


class PaymentSystemDatasource(DictDatasource):
    table = db.PaymentSystem
    model = PaymentSystem
