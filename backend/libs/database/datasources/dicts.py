from libs.database.models import UserType, Tariff, PaymentSystem
from libs.database import tables as db

from .base import Base


class UserTypeDatasource(Base):
    table = db.UserType
    model = UserType


class TariffDatasource(Base):
    table = db.Tariff
    model = Tariff


class PaymentSystemDatasource(Base):
    table = db.PaymentSystem
    model = PaymentSystem
