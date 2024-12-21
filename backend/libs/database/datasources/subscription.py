from datetime import datetime

from dateutil.relativedelta import relativedelta

from sqlalchemy import update

from libs.database.models import Subscription, Payment
from libs.database import tables as db
from .base import Base


# TODO доделать формирование подписки из ссылки. Аналогично пустые платежи из ссылки
class SubscriptionDatasource(Base):
    table_name = db.Subscription
    model = Subscription

    async def _save(self, subscription: db.Subscription) -> Subscription:
        model_object = Subscription.model_validate(subscription)

        if subscription.id:
            query = (
                update(db.Subscription)
                .where(db.Subscription.id == subscription.id)
                .values(
                    end_at=subscription.end_at
                )
            )
            await self.session.execute(query)

        else:
            self.session.add(subscription)
        await self.session.commit()

        return model_object

    async def save_from_payment(self, payment: Payment) -> Subscription:
        subscription = await self.get(user_profile_id=payment.user.id, channel_id=payment.channel.id)

        if not subscription:
            subscription = db.Subscription(user_profile_id=payment.user.id,
                                           channel_id=payment.channel.id,
                                           end_at=datetime.now())

        subscription.end_at = max(payment.end_at, subscription.end_at) + relativedelta(months=1)

        subscription_model = await self._save(subscription)

        return subscription_model
