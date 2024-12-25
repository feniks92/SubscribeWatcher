from enum import StrEnum

from typing import Union
from sqlalchemy import Column, DateTime, Integer, func, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey, Index

from libs.database.tables.base import Base


class BotType(StrEnum):
    GIGABOT = 'gigabot'  # Главный бот. Один на весь проект
    BOT = 'bot'


class UserType(StrEnum):
    GIGACHAD = 'gigachad'  # тот, кто может управлять главным ботом (суперюзер)
    SUBSCRIBER = 'subscriber'  # тот, кто покупает подписки
    OWNER = 'owner'  # администратор/владелец каналов, подботов


UserProfileType = Union[BotType, UserType]


class UserProfile(Base):
    __tablename__ = 'user_profile'
    __table_args__ = (
        Index('ix_user_profile_user_id_user_type',
              'user_id', 'user_type',
              unique=False),
    )

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    user = relationship('User', back_populates='user_profile')

    user_type = Column(String, nullable=False)

    inserted_at = Column('inserted_at', DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column('updated_at', DateTime(timezone=True), nullable=False,
                        server_default=func.now(), onupdate=func.now())
