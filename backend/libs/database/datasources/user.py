from sqlalchemy import update

from libs.database.models import UserProfile, User
from libs.database import tables as db
from .base import Base


class UserDatasource(Base):
    table_name = db.User
    model = User

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
                    user_tg_id=user_tg_id,
                    settings=settings
                )
            )

        return self.model.model_validate(await self.get(user_tg_id=user_tg_id))


class UserProfileDatasource(Base):
    table_name = db.UserProfile
    model = UserProfile

    async def save(self,
                   user_id: int,
                   profile_type_id: int):
        existing_profile = await self.get(user_id=user_id, user_type_id=profile_type_id)

        if not existing_profile:
            self.session.add(
                db.UserProfile(
                    user_id=user_id,
                    user_type_id=profile_type_id
                )
            )

        await self.session.commit()
