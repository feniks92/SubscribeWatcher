from sqlalchemy import Integer, String, Boolean, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.schema import Index

from libs.database.tables.base import Base


class Tariff(Base):
    _tablename__ = 'tariff'
    __table_args__ = (
        Index('ix_project_id_tariff_active', 'project_id', 'active'),
    )

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False, server_default='')
    active = Column(Boolean, nullable=False, server_default=expression.true())
    project_id = Column(Integer, ForeignKey('project.id'), nullable=False)
    project = relationship('Project', back_populates='tariffs')
    payment_amount = Column(Integer, nullable=False, server_default='250')
    subscribe_duration = Column(Integer, nullable=False, server_default='1')
