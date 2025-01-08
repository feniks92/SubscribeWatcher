from typing import Optional

from fastapi import BackgroundTasks

from libs import logging

from libs.database.sql_alchemy import Session
from libs.database.datasources.user import UserDatasource
from libs.database.models import User, ProfileTypes, UserProfile, Subscription
from libs.dependencies import ParticipantsInfo

log = logging.getLogger('general_handler')


class BaseHandler:
    user: User | None = None
    bot: User | None = None

    def __init__(self, session: Session, participants: ParticipantsInfo):
        self.session = session
        self.participants = participants

    async def get_roles(self):
        self.user = await UserDatasource(self.session).get(user_tg_id=self.participants.user.telegram_id)
        self.bot = await UserDatasource(self.session).get(user_tg_id=self.participants.bot_id)

    def user_owner_profile(self) -> Optional[UserProfile]:
        if self.bot and self.user:
            prof = self.user.get_profile_by_type_name(ProfileTypes.OWNER)

            if prof.user_is_project_owner(self.bot.user_profile[0].projects[0]):
                return prof

    def user_subscription(self) -> Optional[Subscription]:
        if self.bot and self.user:
            return self.user.get_profile_by_type_name().user_project_subscription(
                project_id=self.bot.user_profile[0].projects[0].id)

    def user_gigachad_profile(self) -> Optional[UserProfile]:
        if self.bot and self.user:
            return self.user.get_profile_by_type_name(ProfileTypes.GIGACHAD)

    def gigabot_profile(self) -> Optional[UserProfile]:
        if self.bot:
            return self.bot.get_profile_by_type_name(ProfileTypes.GIGABOT)


# TODO пока не придумал что делать если пришли с бота, которого у нас нет.
# Этот случай будет возвращать тип пользователя None и тип бота None
class AuthorizeHandler(BaseHandler):
    metrics_prefix = 'authorize'

    async def handle(self, bg_tasks: BackgroundTasks):
        await self.get_roles()

        prof = self.user_gigachad_profile() or self.user_owner_profile()
        user_type = prof.user_type

        bot_type = self.bot.get_all_user_profiles_names()
        bot_type = ProfileTypes.GIGABOT if ProfileTypes.GIGABOT in bot_type else ProfileTypes.BOT
        return user_type, bot_type
