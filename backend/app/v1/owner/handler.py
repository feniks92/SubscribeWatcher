from fastapi import BackgroundTasks, HTTPException

from libs import logging

from app.v1.general.handler import BaseHandler
from libs.database.models import Project
from libs.database.datasources.project import ProjectDatasource
from libs.database.datasources.dicts import GigaTariffDatasource
from libs.database.datasources.user import UserDatasource, UserProfileDatasource
from libs.database.models.user import ProfileTypes
from .schemas import GigaTariffItem, ProjectRequest

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

    async def create(self, bg_tasks: BackgroundTasks, project_data: ProjectRequest) -> Project | HTTPException:
        await self.get_roles()

        if not (bot_prof := self.gigabot_profile()):
            raise HTTPException(status_code=401, detail='Your bot have not enough permission')

        # секция валидации
        # TODO добавить настройки по умолчанию
        if not self.user:
            self.user = await UserDatasource(session=self.session).save(
                user_tg_id=self.participants.user.telegram_id,
                settings={}
            )

        if not (prof := self.user_owner_profile()):
            prof = await UserProfileDatasource(session=self.session).save(
                user_id=self.user.id,
                profile_type=ProfileTypes.OWNER
            )

        project = ProjectDatasource(session=self.session).get(owner_id=prof.id, name=project_data.name)
        if project:
            raise HTTPException(status_code=409, detail='Project already exists')

        return await ProjectDatasource(session=self.session).create_or_update_project(
            name=project_data.name,
            owner_id=prof.id,
            tariff_id=project_data.tariff_id,
            payment_destination=project_data.payment_destination,
            admin_bot_id=project_data.admin_bot_id,
            payment_system_id=project_data.payment_system_id,
        )


class TariffHandler(BaseHandler):
    metrics_prefix = 'tariff'

    async def giga_tariffs(self, bg_tasks: BackgroundTasks) -> list[GigaTariffItem]:
        await self.get_roles()

        return await GigaTariffDatasource(session=self.session).get_all()
