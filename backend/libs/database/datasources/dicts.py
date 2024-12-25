from libs.database.models import GigaTariff, PaymentSystem
from libs.database import tables as db

from .base import Base

class GigaTariffDatasource(Base):
    table = db.GigaTariff
    model = GigaTariff


class PaymentSystemDatasource(Base):
    table = db.PaymentSystem
    model = PaymentSystem
