from datetime import datetime
from enum import StrEnum

from pydantic import Field

from .base import DatabaseBaseModel as BaseModel


class ProfileTypes(StrEnum):
    BOT = 'bot'
    ADMIN = 'admin'
    SUBSCRIBER = 'subscriber'
    OWNER = 'owner'


class UserProfile(BaseModel):
    id: int = Field(title='User profile inner Id')
    user_type: str = Field(title='User type')
    inserted_at: datetime = Field(title="Inserted At")
    updated_at: datetime = Field(title="Updated At")


class User(BaseModel):
    id: int = Field(title='User inner Id')
    user_telegram_id: str = Field(title='User Telegram Id')
    settings: dict | None = Field(None, title='Settings')
    inserted_at: datetime = Field(title='Inserted at')
    updated_at: datetime = Field(title='Updated at')
    user_profile: list[UserProfile] = Field((), title='User Profile')

    def get_profile_by_type_name(self, profile_type_name):
        for profile in self.user_profile:
            if profile.user_type == profile_type_name:
                return profile
