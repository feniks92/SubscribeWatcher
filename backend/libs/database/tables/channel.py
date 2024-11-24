from sqlalchemy import Column, DateTime, Integer, func, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey, Index

from libs.database.tables import Base


class Channel(Base):
    __tablename__ = 'channel'

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, nullable=False, index=True)

    owner_id = Column(Integer, ForeignKey('user_profile.id'), nullable=False)
    owner = relationship('UserProfile', back_populates='channels_owner')

    admin_bot_id = Column(Integer, ForeignKey('user_profile.id'), nullable=False)
    admin_bot = relationship('UserProfile', back_populates='channels_admin')

    tariff_id = Column(Integer, ForeignKey('tariff.id'), nullable=False)
    tariff = relationship('Tariff', back_populates='channels_tariff')

    payment_amount = Column(Integer, nullable=False, server_default='250')
    payment_destination = Column(String, nullable=False, server_default='')

    payment_system_id = Column(Integer, ForeignKey('payment_system.id'), nullable=False)
    payment_system = relationship('PaymentSystem', back_populates='channels_payment_system')

    joined_at = Column('joined_at', DateTime, nullable=False, server_default=func.now())
    updated_at = Column('updated_at', DateTime, nullable=False,
                        server_default=func.now(), nupdate=func.now())

    __table_args__ = (
        Index('ix_channel_owner_id_telegram_id', owner_id, telegram_id),

        Index('ix_channel_telegram_id_tariff_id', telegram_id, tariff_id),
    )
