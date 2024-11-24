from sqlalchemy import Column, DateTime, Integer, func
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey, Index

from libs.database.tables.base import Base


class UserProfile(Base):
    __tablename__ = 'user_profile'
    __table_args__ = (
        Index('ix_user_profile_user_id_user_type_id',
              'user_id', 'user_type_id',
              unique=False),
    )

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    user = relationship('User', back_populates='user_profile')

    user_type_id = Column(Integer, ForeignKey('user_type.id'), nullable=False)
    user_type = relationship('UserType', back_populates='user_profile')

    inserted_at = Column('inserted_at', DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column('updated_at', DateTime(timezone=True), nullable=False,
                        server_default=func.now(), onupdate=func.now())

