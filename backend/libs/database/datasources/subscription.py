from typing import Optional

from sqlalchemy import update

from libs.database.models import Subscription
from libs.database import tables as db
from .base import Base

# TODO доделать формирование подписки из платежа и ссылки. Аналогично пустые платежи из ссылки
class SubscriptionDatasource(Base):
    table_name = db.Subscription
    model = Subscription

    async def _save(self, subscription: db.Subscription) -> Subscription:
        model_object = Subscription.model_validate(subscription)

        if subscription.id:
            update(db.Subscription)
            .where(db.Subscription.id == subscription.id)
            .values