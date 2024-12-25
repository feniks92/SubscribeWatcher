from sqlalchemy import Column, DateTime, Integer, func, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey, Index

from libs.database.tables.base import Base


# TODO добавить токен управления ботом. Продумать смену токена бота
class Project(Base):
    __tablename__ = 'project'

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)

    owner_id = Column(Integer, ForeignKey('user_profile.id'), nullable=False)
    owner = relationship('UserProfile', back_populates='projects')

    admin_bot_id = Column(Integer, ForeignKey('user_profile.id'), nullable=False)
    admin_bot = relationship('UserProfile', back_populates='projects')

    tariff_id = Column(Integer, ForeignKey('giga_tariff.id'), nullable=False)
    tariff = relationship('GigaTariff', back_populates='projects')

    payment_destination = Column(String, nullable=False, server_default='')

    payment_system_id = Column(Integer, ForeignKey('payment_system.id'), nullable=False)
    payment_system = relationship('PaymentSystem', back_populates='projects')

    joined_at = Column('joined_at', DateTime, nullable=False, server_default=func.now())
    updated_at = Column('updated_at', DateTime, nullable=False,
                        server_default=func.now(), onupdate=func.now())

    channels = relationship('Channel', back_populates='project')

    __table_args__ = (
        Index('ix_project_owner_id_name', owner_id, name),

        Index('ix_project_name_tariff_id', name, tariff_id),
    )


class Channel(Base):
    __tablename__ = 'channel'

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)

    project_id = Column(Integer, ForeignKey('project.id'), nullable=False)
    project = relationship('Project', back_populates='channels')
