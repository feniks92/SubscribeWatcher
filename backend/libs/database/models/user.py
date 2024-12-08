from datetime import datetime

from pydantic import Field

from .base import DatabaseBaseModel as BaseModel
from .dicts import UserType


class User(BaseModel):
    id: int = Field(title='User inner Id')
    user_telegram_id: str = Field(title='User Telegram Id')
    settings: dict | None = Field(None, title='Settings')
    inserted_at: datetime = Field(title='Inserted at')
    updated_at: datetime = Field(title='Updated at')


class UserProfile(BaseModel):
    id: int = Field(title='User profile inner Id')
    user: User = Field(title='User profile')
    user_type: UserType = Field(title='User type')
    inserted_at: datetime = Field(title="Inserted At")
    updated_at: datetime = Field(title="Updated At")