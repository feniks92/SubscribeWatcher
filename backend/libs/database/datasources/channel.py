from typing import Optional

from sqlalchemy import update

from libs.database.models import Channel, ProfileTypes
from libs.database import tables as db
from .base import Base
from .user import UserDatasource, UserProfileDatasource


class ChannelDatasource(Base):
    table_name = db.Channel
    model = Channel

    async def _save(self, channel: db.Channel) -> Channel:
        model_object = Channel.model_validate(channel)

        if channel.id:
            query = (
                update(db.Channel)
                .where(db.Channel.id == channel.id)
                .values(owner_id=channel.owner_id,
                        name=channel.name,
                        owner=channel.owner,
                        admin_bot_id=channel.admin_bot_id,
                        admin_bot=channel.admin_bot,
                        tarrif_id=channel.tariff_id,
                        tariff=channel.tariff,
                        payment_amount=channel.payment_amount,
                        payment_destination=channel.payment_destination,
                        payment_system_id=channel.payment_system_id,
                        payment_system=channel.payment_system)
            )
            await self.session.execute(query)

        else:
            self.session.add(channel)
        await self.session.commit()

        return model_object

    async def change_owner(self, channel_telegram_id: int,
                           new_telegram_owner_id: str) -> Channel:
        channel = await self.get(telegram_id=channel_telegram_id)
        new_owner = await UserDatasource(self.session).get(user_tg_id=new_telegram_owner_id)
        if not new_owner:
            new_owner = await UserDatasource(self.session).save(user_tg_id=new_telegram_owner_id,
                                                                settings={'lang': 'RU'})
        new_owner_profile = new_owner.get_profile_by_type_name(ProfileTypes.OWNER)
        if not new_owner_profile:
            new_owner_profile = await UserProfileDatasource(self.session).save(user_id=new_owner.id,
                                                                               profile_type=ProfileTypes.OWNER)
        channel.owner = new_owner_profile
        channel.owner_id = new_owner_profile.id

        return await self._save(channel=channel)

    async def create_or_update_channel(self,
                                       telegram_id: str,
                                       name: Optional[str] = None,
                                       owner_id: Optional[int] = None,
                                       admin_bot_id: Optional[int] = None,
                                       tariff_id: Optional[int,] = None,
                                       payment_amount: Optional[int] = None,
                                       payment_destination: Optional[str] = None,
                                       payment_system_id: Optional[int] = None) -> Channel:

        channel = await self.get(telegram_id=telegram_id)

        if channel:
            channel.owner_id = owner_id or channel.owner_id
            channel.name = name or channel.name
            channel.admin_bot_id = admin_bot_id or channel.admin_bot_id
            channel.tariff_id = tariff_id or channel.tariff_id
            channel.payment_amount = payment_amount or channel.payment_amount
            channel.payment_destination = payment_destination or channel.payment_destination
            channel.payment_system_id = payment_system_id or channel.payment_system_id

        if not channel:
            channel = db.Channel(telegram_id=telegram_id,
                                 name=name,
                                 owner_id=owner_id,
                                 admin_bot_id=admin_bot_id,
                                 tariff_id=tariff_id,
                                 payment_amount=payment_amount,
                                 payment_destination=payment_destination,
                                 payment_system_id=payment_system_id)

        channel_model = await self._save(channel=channel)

        return channel_model
