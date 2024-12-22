from pydantic import BaseModel, Field
from pydantic.dataclasses import dataclass
from datetime import datetime
from typing import Optional, TypeVar

from fastapi import Depends, Header, Query, Body
from fastapi.exceptions import HTTPException

from starlette import status


class UserInfo(BaseModel):
    first_name: str = Field(...)
    last_name: str = Field(...)
    telegram_id: str = Field(..., alias='id')
    is_bot: Optional[bool] = Field(False)
    is_premium: Optional[bool] = Field(False)
    language_code: Optional[str] = Field('ru')


class Tariff(BaseModel):
    ...

@dataclass(config={'populate_by_name': True, 'coerce_numbers_to_str': True})
class ParticipantsInfo:
    user: UserInfo = Body(...)
    bot_id: str = Body(..., alias='bot_id')


class AuthorizeResponse(BaseModel):
    is_admin: bool = Field(False, alias='is_admin')
    is_owner: bool = Field(False, alias='is_owner')


class ChannelResponse(BaseModel):
    is_admin: bool = Field(False, alias='is_admin')
    is_owner: bool = Field(False, alias='is_owner')
    is_admin_bot: bool = Field(False, alias='is_bot_admin')
    admin_bot_id: int = Field(..., alias='admin_bot_id')
    name: str = Field(..., alias='name')
    telegram_id: str = Field(..., alias='id')
    tariff: list[Tariff] = Field(..., alias='tariff')


class SubscriptionInfoResponse(BaseModel):
    tariffs: list[Tariff] = Field(..., alias='tariffs')
    subscription_end: Optional[datetime] = Field(None, alias='subscription_end')
