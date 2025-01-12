from fastapi import BackgroundTasks

from libs import logging
from libs.database.models.user import ProfileTypes
from libs.database.datasources.user import UserDatasource, UserProfileDatasource

from app.v1.general.handler import BaseHandler

log = logging.getLogger('watcher_handler')


class SubscriptionHandler(BaseHandler):
    metrics_prefix = 'subscription'

    async def _check_user(self):
        await self.get_roles()

        if not self.user:
            self.user = await UserDatasource(session=self.session).save(
                user_tg_id=self.participants.user.telegram_id,
                settings={}
            )

        if not self.user.get_profile_by_type_name(ProfileTypes.SUBSCRIBER):
            prof = await UserProfileDatasource(session=self.session).save(
                user_id=self.user.id,
                profile_type=ProfileTypes.SUBSCRIBER
            )
            self.user.user_profile.append(prof)

    async def get_subscription_info(self, bg_tasks: BackgroundTasks):
        await self._check_user()

        return self.user_subscription()

    async def get_tariff_list(self, bg_tasks: BackgroundTasks):
        await self._check_user()

        project = self.bot.get_profile_by_type_name(ProfileTypes.BOT).projects[0]

        return project.tariffs
