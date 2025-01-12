from dataclasses import dataclass

from fastapi import Body
from pydantic import BaseModel, Field

from datetime import datetime
from typing import Optional


class SubscriptionItem(BaseModel):
    id: Optional[str] = Field(default_factory=str, alias="id")
    start_at: Optional[datetime] = Field(default=None, description='дата когда подписка впервые была оформлена')
    update_at: Optional[datetime] = Field(default=None, title='Дата последнего обновления подписки (дата платежа)')
    end_at: Optional[datetime] = Field(default=None, title='Дата окончания подписки')


class SubscriptionInfoResponse(BaseModel):
    rq_id: Optional[str] = Field(None, description='Идентификатор запроса',
                                 examples=['698c6fc1-b284-4f4b-b9a6-f317b1bf0811'], alias='rqId')
    subscription: Optional[SubscriptionItem] = Field(None, alias='subscription')


@dataclass
class SubscriptionRenewRequest:
    tariff_id: int = Body(..., alias='tariff_id')
