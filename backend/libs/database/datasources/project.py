from typing import Optional

from sqlalchemy import update

from libs.database.models import Project, ProfileTypes
from libs.database import tables as db
from .base import Base
from .user import UserDatasource, UserProfileDatasource


class ProjectDatasource(Base):
    table_name = db.Project
    model = Project
    _selectinload = (db.Project.channels, db.Tariff)

    async def _save(self, project: db.Project) -> Project:
        model_object = Project.model_validate(project)

        if project.id:
            query = (
                update(db.Project)
                .where(db.Project.id == project.id)
                .values(owner_id=project.owner_id,
                        name=project.name,
                        owner=project.owner,
                        admin_bot_id=project.admin_bot_id,
                        admin_bot=project.admin_bot,
                        tarrif_id=project.tariff_id,
                        tariff=project.tariff,
                        payment_destination=project.payment_destination,
                        payment_system_id=project.payment_system_id,
                        payment_system=project.payment_system)
            )
            await self.session.execute(query)

        else:
            self.session.add(project)
        await self.session.commit()

        return model_object

    async def change_owner(self, project_id: int,
                           new_telegram_owner_id: str) -> Project:
        project = await self.get(id=project_id)
        new_owner = await UserDatasource(self.session).get(user_tg_id=new_telegram_owner_id)
        if not new_owner:
            new_owner = await UserDatasource(self.session).save(user_tg_id=new_telegram_owner_id,
                                                                settings={'lang': 'RU'})
        new_owner_profile = new_owner.get_profile_by_type_name(ProfileTypes.OWNER)
        if not new_owner_profile:
            new_owner_profile = await UserProfileDatasource(self.session).save(user_id=new_owner.id,
                                                                               profile_type=ProfileTypes.OWNER)
        project.owner = new_owner_profile
        project.owner_id = new_owner_profile.id

        return await self._save(project=project)

    async def create_or_update_project_by_name(self,
                                               name: str,
                                               owner_id: int,
                                               admin_bot_id: Optional[int] = None,
                                               tariff_id: Optional[int] = None,
                                               payment_destination: Optional[str] = None,
                                               payment_system_id: Optional[int] = None) -> Project:

        project = await self.get(name=name, owner_id=owner_id)

        if project:
            project.owner_id = owner_id or project.owner_id
            project.name = name or project.name
            project.admin_bot_id = admin_bot_id or project.admin_bot_id
            project.tariff_id = tariff_id or project.tariff_id
            project.payment_destination = payment_destination or project.payment_destination
            project.payment_system_id = payment_system_id or project.payment_system_id

        if not project:
            project = db.Project(name=name,
                                 owner_id=owner_id,
                                 admin_bot_id=admin_bot_id,
                                 tariff_id=tariff_id,
                                 payment_destination=payment_destination,
                                 payment_system_id=payment_system_id)

        project_model = await self._save(project=project)

        return project_model

    async def update_by_id(self,
                           project_id: int,
                           name: Optional[str] = None,
                           admin_bot_id: Optional[int] = None,
                           tariff_id: Optional[int] = None,
                           payment_destination: Optional[str] = None,
                           payment_system_id: Optional[int] = None
                           ) -> Project | None:

        project = await self.get(id=project_id)

        if not project:
            return None

        project.name = name or project.name
        project.admin_bot_id = admin_bot_id or project.admin_bot_id
        project.tariff_id = tariff_id or project.tariff_id
        project.payment_destination = payment_destination or project.payment_destination
        project.payment_system_id = payment_system_id or project.payment_system_id

        project_model = await self._save(project=project)

        return project_model
