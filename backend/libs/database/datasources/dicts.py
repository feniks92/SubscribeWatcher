from libs.database.models import Tariff, PaymentSystem
from libs.database import tables as db

from .base import Base

class TariffDatasource(Base):
    table = db.Tariff
    model = Tariff


class PaymentSystemDatasource(Base):
    table = db.PaymentSystem
    model = PaymentSystem
