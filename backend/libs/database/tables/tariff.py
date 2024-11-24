from sqlalchemy import Boolean, Column, Integer, String, Float
from sqlalchemy.sql import expression
from sqlalchemy.sql.schema import Index

from libs.database.tables import Base


class Tariff(Base):
    __tablename__ = 'tariff'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=False, server_default='')
    active = Column(Boolean, nullable=False, server_default=expression.true())
    tariff_fee = Column(Float, nullable=False, server_default='0.5')

    __table_args__ = (
        Index('ix_tariff_active', active),
    )