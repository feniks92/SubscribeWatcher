from typing import Optional

from sqlalchemy import update

from libs.database.models import Payment
from libs.database import tables as db
from .base import Base


class PaymentDatasource(Base):
    table_name = db.Payment
    model = Payment

    async def save(self):
        pass