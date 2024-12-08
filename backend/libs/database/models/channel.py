from pydantic import Field

from .base import DatabaseBaseModel as BaseModel

class Channel(BaseModel):
    telegram_id: int = Field(title='Channel telegram id')
    id: int = Field(title='Channel inner id')
    owner_id: int = Field(None, title='Channel owner id')
    owner: str | None = Field(title='Channel owner')
