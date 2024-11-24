from sqlalchemy import Column, DateTime, Integer, String, func

from libs.database.tables.base import Base


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, index=True)
    user_tg_id = Column(String, nullable=False, unique=True, index=True)

    inserted_at = Column('inserted_at', DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column('updated_at', DateTime(timezone=True), nullable=False,
                        server_default=func.now(), onupdate=func.now())
