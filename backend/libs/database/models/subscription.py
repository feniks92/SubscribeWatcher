from datetime import datetime

from pydantic import Field

from .base import DatabaseBaseModel as BaseModel
from .project import Project
# from .user import UserProfile


class Subscription(BaseModel):
    id: str = Field(title='Идентификатор подписки')
    # user_profile: UserProfile = Field(title='Профиль пользователя')
    project: Project = Field(title='Канал подписки')
    start_at: datetime = Field(title='started at')
    update_at: datetime= Field(title='updated at')
    end_at: datetime = Field(title='ended at')
