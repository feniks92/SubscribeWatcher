import uuid

from sqlalchemy import Column, Integer, func, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey, Index

from libs.database.tables.base import Base


class Subscription(Base):
    __tablename__ = 'subscription'

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, unique = True, default = uuid.uuid4)

    user_profile_id = Column(Integer, ForeignKey('user_profile.id'), nullable=False)
    user_profile = relationship('UserProfile', back_populates='subscribes')

    project_id = Column(Integer, ForeignKey('project.id'), nullable=False)
    project = relationship('Project', back_populates='subscribes')

    start_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    update_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    end_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index('ix_subscribe_update_at_end_at', update_at, end_at),

        Index('ix_subscribe_project_id_user_profile_id', project_id, user_profile_id),
    )
