from pydantic import BaseModel, Field
from pydantic.dataclasses import dataclass

from fastapi import Depends, Header, Query, Body
from fastapi.exceptions import HTTPException

from typing import Optional

from starlette import status


class UserInfo(BaseModel):
    first_name: str = Field(...)
    last_name: str = Field(...)
    telegram_id: str = Field(..., alias='id')
    is_bot: Optional[bool] = Field(False)
    is_premium: Optional[bool] = Field(False)
    language_code: Optional[str] = Field('ru')


@dataclass(config={'populate_by_name': True, 'coerce_numbers_to_str': True})
class ParticipantsInfo:
    user: UserInfo = Body(...)
    bot_id: str = Body(..., alias='bot_id')
