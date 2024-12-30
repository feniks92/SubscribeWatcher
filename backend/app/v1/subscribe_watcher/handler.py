from fastapi import BackgroundTasks

from libs import logging

from app.v1.general.handler import BaseHandler

log = logging.getLogger('watcher_handler')


class SubscriptionHandler(BaseHandler):
    metrics_prefix = 'subscription'

    async def handle(self, bg_tasks: BackgroundTasks):
        await self.get_roles()

        if subscription := self.user_subscription():
            return subscription.end_at
