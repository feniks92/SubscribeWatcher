from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import Field, field_validator

from .base import DatabaseBaseModel as BaseModel


class User(BaseModel):
    id: int = Field(title='User inner Id')
    user_telegram_id: str = Field(title='User Telegram Id')
    inserted_at: datetime = Field(title='Inserted at')
    updated_at: datetime = Field(title='Updated at')


class UserProfile(BaseModel):
    id: int = Field(title='User profile inner Id')
    user