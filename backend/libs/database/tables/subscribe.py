import uuid

from sqlalchemy import Column, Integer, func, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey, Index

from libs.database.tables import Base


class Subscribe(Base):
    __tablename__ = 'subscribe'

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, unique = True, default = uuid.uuid4)

    user_profile_id = Column(Integer, ForeignKey('user_profile.id'), nullable=False)
    user_profile = relationship('UserProfile', back_populates='subscribes')

    channel_id = Column(Integer, ForeignKey('channels.id'), nullable=False)
    channel = relationship('Channel', back_populates='subscribes')

    start_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    update_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    end_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index('ix_subscribe_update_at_end_at', update_at, end_at),

        Index('ix_subscribe_channel_id_user_profile_id', channel_id, user_profile_id),
    )
