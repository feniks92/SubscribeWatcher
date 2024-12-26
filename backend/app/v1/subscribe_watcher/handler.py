from typing import Optional, Type

from fastapi import BackgroundTasks

from libs import logging
from libs.database.sql_alchemy import Session
from libs.database.datasources.user import UserDatasource
from libs.database.models import User, ProfileTypes
from libs.dependencies import ParticipantsInfo

log = logging.getLogger('watcher_handler')

class BaseHandler:
    user: User | None = None
    bot: User | None = None

    def __init__(self, session: Session, participants: ParticipantsInfo):
        self.session = session
        self.participants = participants

    async def get_roles(self):
        self.user = await UserDatasource(self.session).get(user_tg_id=self.participants.user.telegram_id)
        self.bot = await UserDatasource(self.session).get(user_tg_id=self.participants.bot_id)


class AuthorizeHandler(BaseHandler):
    metrics_prefix = 'authorize'

    async def handle(self, bg_tasks: BackgroundTasks):
        await self.get_roles()
        user_types = self.user.get_all_user_profiles_names()
        bot_types = self.bot.get_all_user_profiles_names()
        bot_types = ProfileTypes.GIGABOT if ProfileTypes.GIGABOT in bot_types else ProfileTypes.BOT
        return user_types, bot_types


class ProjectHandler(BaseHandler):
    metrics_prefix = 'project'

    async def handle(self, bg_tasks: BackgroundTasks):
        await self.get_roles()


class SubscriptionHandler(BaseHandler):
    metrics_prefix = 'subscription'

    async def handle(self, bg_tasks: BackgroundTasks):
        ...