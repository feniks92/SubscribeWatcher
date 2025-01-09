from typing import Optional
from sqlalchemy import update

from libs.database.models import TariffModel
from libs.database import tables as db
from .base import Base


class TariffDatasource(Base):
    table_name = db.Tariff
    model = TariffModel
    _selectinload = (db.Project,)

    async def _save(self, tariff: db.Tariff) -> TariffModel:
        model_object = tariff.model_validate(tariff)

        if tariff.id:
            query = (
                update(db.Tariff)
                .where(db.Tariff.id == tariff.id)
                .values(name=tariff.name,
                        payment_amount=tariff.payment_amount,
                        description=tariff.description,
                        subscribe_duration=tariff.subscribe_duration,
                        project_id=tariff.project_id)
            )
            await self.session.execute(query)

        else:
            self.session.add(tariff)
        await self.session.commit()

        return model_object

    async def update_tariff(self,
                            tariff_id: int,
                            name: Optional[str] = None,
                            description: Optional[str] = None,
                            payment_amount: Optional[int] = None,
                            subscribe_duration: Optional[int] = None,
                            ):
        tariff = await self.get(id=tariff_id)

        tariff.name = name or tariff.name
        tariff.description = description or tariff.description
        tariff.payment_amount = payment_amount or tariff.payment_amount
        tariff.subscribe_duration = subscribe_duration or tariff.subscribe_duration

        tariff_model = await self._save(tariff)

        return tariff_model
