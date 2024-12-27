from sqlalchemy import update

from libs.database.models import UserProfile, User, ProfileTypes
from libs.database import tables as db
from .base import Base


class UserDatasource(Base):
    table_name = db.User
    model = User
    _selectinload = (db.User.user_profile, db.User.user_profile.projects)  # подтягивать проекты

    async def save(self,
                   user_tg_id: str,
                   settings: dict
                   ) -> User:

        existing_user = await self.get(user_tg_id=user_tg_id)

        if existing_user:
            query = (
                update(self.table)
                .where(user_tg_id=user_tg_id)
                .values(settings=settings)
            )
            await self.session.execute(query)
        else:
            self.session.add(
                self.table_name(
                    settings=settings
                )
            )

        await self.session.commit()

        return self.model.model_validate(await self.get(user_tg_id=user_tg_id))


class UserProfileDatasource(Base):
    table_name = db.UserProfile
    model = UserProfile

    async def save(self,
                   user_id: int,
                   profile_type: ProfileTypes) -> UserProfile:
        existing_profile = await self.get(user_id=user_id, user_type=profile_type)

        if not existing_profile:
            self.session.add(
                db.UserProfile(
                    user_id=user_id,
                    user_type=profile_type
                )
            )

        await self.session.commit()

        return self.model.model_validate(await self.get(user_id=user_id, user_type=profile_type))
