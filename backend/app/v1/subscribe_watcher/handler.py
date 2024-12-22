from typing import Optional, Type

from fastapi import BackgroundTasks

from libs import logging
from libs.database.sql_alchemy import Session

from .schemas import ParticipantsInfo

log = logging.getLogger('watcher_handler')

class BaseHandler:
    def __init__(self, session: Session, participants: ParticipantsInfo):
        self.session = session
        self.participants = participants


class AuthorizeHandler(BaseHandler):
    metrics_prefix = 'authorize'

    async def handle(self, bg_tasks: BackgroundTasks):
        ...


class ChannelHandler(BaseHandler):
    metrics_prefix = 'channel'

    async def handle(self, bg_tasks: BackgroundTasks):
        ...


class SubscriptionHandler(BaseHandler):
    metrics_prefix = 'subscription'

    async def handle(self, bg_tasks: BackgroundTasks):
        ...