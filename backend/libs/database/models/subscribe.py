from datetime import datetime

from pydantic import Field

from .base import DatabaseBaseModel as BaseModel
from .channel import Channel
from .user import UserProfile


class Subscribe(BaseModel):
    id: str = Field(title='Идентификатор подписки')
    user_profile: UserProfile = Field(title='Профиль пользователя')
    channel: Channel = Field(title='Канал подписки')
    start_at: datetime = Field(title='started at')
    update_at: datetime= Field(title='updated at')
    end_at: datetime = Field(title='ended at')
