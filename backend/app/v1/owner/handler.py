from fastapi import BackgroundTasks, HTTPException

from libs import logging

from app.v1.general.handler import BaseHandler
from libs.database.models import Project

log = logging.getLogger('owner_handler')

class ProjectHandler(BaseHandler):
    metrics_prefix = 'project'

    async def handle(self, bg_tasks: BackgroundTasks):
        await self.get_roles()

        if prof := self.user_owner_profile():
            return prof.projects

    async def handle_one(self, bg_tasks: BackgroundTasks, project_id: int) -> Project | HTTPException:
        await self.get_roles()
        if prof := self.user_owner_profile():
            return prof.user_get_project_by_id(project_id)

        raise HTTPException(status_code=401, detail='Not enough permission')