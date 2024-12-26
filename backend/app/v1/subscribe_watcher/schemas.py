from pydantic import BaseModel, Field

from datetime import datetime
from typing import Optional

from libs.database.tables.user_profile import UserType, BotType


class Tariff(BaseModel):
    ...


class AuthorizeResponse(BaseModel):
    user_type: list[UserType] = Field(...)
    bot_type: BotType = Field(...)


class ProjectResponse(AuthorizeResponse):
    admin_bot_id: int = Field(..., alias='admin_bot_id')
    name: str = Field(..., alias='name')
    telegram_id: str = Field(..., alias='id')
    tariff: list[Tariff] = Field(..., alias='tariff')


class SubscriptionInfoResponse(BaseModel):
    tariff: Tariff = Field(..., alias='tariffs')
    subscription_end: Optional[datetime] = Field(None, alias='subscription_end')
