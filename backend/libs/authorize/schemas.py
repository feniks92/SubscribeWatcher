from pydantic import BaseModel, Field

from libs.database.tables.user_profile import UserType, BotType


class AuthorizeItem(BaseModel):
    user_type: list[UserType] = Field(...)
    bot_type: BotType = Field(...)
