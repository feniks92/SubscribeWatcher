import uuid

from sqlalchemy import Column, DateTime, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey, Index

from libs.database.tables.base import Base


class Payment(Base):
    __tablename__ = 'payment'

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, unique=True, default=uuid.uuid4)

    external_id = Column(String, index=True, nullable=False)
    status = Column(String, nullable=False, server_default='')

    user_id = Column(Integer, ForeignKey('user_profile.id'), nullable=False)
    user = relationship('UserProfile', back_populates='payments')

    project_id = Column(Integer, ForeignKey('project.id'), nullable=False)
    project = relationship('Project', back_populates='payments')

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index('ix_payment_updated_at_project_id_status', updated_at, project_id, status),
        Index('ix_payment_user_id_project_id', user_id, project_id),
    )