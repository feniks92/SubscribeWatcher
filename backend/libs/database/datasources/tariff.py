from sqlalchemy import update

from libs.database.models import TariffModel
from libs.database import tables as db
from .base import Base


class TariffDatasource(Base):
    table_name = db.Tariff
    model = TariffModel
    _selectinload = (db.Project, )

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
