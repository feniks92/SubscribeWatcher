from datetime import datetime
from enum import StrEnum
from typing import Optional

from pydantic import Field

from .base import DatabaseBaseModel as BaseModel
from .project import Project
from .subscription import Subscription


# TODO переделать на единый енам с тем который в моделях. Н без циклического импорта
class ProfileTypes(StrEnum):
    GIGABOT = 'gigabot'  # Главный бот. Один на весь проект
    BOT = 'bot'
    GIGACHAD = 'gigachad'  # тот, кто может управлять главным ботом (суперюзер)
    SUBSCRIBER = 'subscriber'  # тот, кто покупает подписки
    OWNER = 'owner'  # администратор/владелец каналов, подботов


class UserProfile(BaseModel):
    id: int = Field(title='User profile inner Id')
    user_type: str = Field(title='User type')
    inserted_at: datetime = Field(title="Inserted At")
    updated_at: datetime = Field(title="Updated At")
    projects: Optional[list[Project]] = Field(default_factory=list, title='User projects')
    subscriptions: Optional[list[Subscription]] = Field(default_factory=list, title='User subscriptions')

    # TODO need refactor
    def user_is_project_owner(self, project: Project) -> bool:
        for proj in self.projects:
            if proj.id == project.id:
                return True
        return False

    def user_project_subscription(self, project_id: int) -> Optional[Subscription]:
        for subscription in self.subscriptions:
            if subscription.id == project_id:
                return subscription


class User(BaseModel):
    id: int = Field(title='User inner Id')
    user_telegram_id: str = Field(title='User Telegram Id')
    settings: dict | None = Field(None, title='Settings')
    inserted_at: datetime = Field(title='Inserted at')
    updated_at: datetime = Field(title='Updated at')
    user_profile: list[UserProfile] = Field((), title='User Profile')

    def get_profile_by_type_name(self, profile_type_name: ProfileTypes = ProfileTypes.SUBSCRIBER):
        for profile in self.user_profile:
            if profile.user_type == profile_type_name:
                return profile

    def get_all_user_profiles_names(self):
        return [profile.user_type for profile in self.user_profile]
