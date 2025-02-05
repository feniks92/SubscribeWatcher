from sqlalchemy import Integer, String, Boolean, Float
from sqlalchemy.sql import expression
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.schema import Index

from libs.database.tables.base import Base


class Dictionary:
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=False, server_default='')


class PaymentSystem(Dictionary, Base):
    __tablename__ = 'payment_system'
    __table_args__ = (
        Index('ix_payment_system_active_name',
              'active',
              'name'
              ),
    )

    active = Column(Boolean, nullable=False, server_default=expression.true())


class GigaTariff(Dictionary, Base):
    __tablename__ = 'giga_tariff'
    __table_args__ = (
        Index('ix_tariff_active', 'active'),
    )

    active = Column(Boolean, nullable=False, server_default=expression.true())
    tariff_fee = Column(Float, nullable=False, server_default='0.5')
