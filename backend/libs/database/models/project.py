from pydantic import Field

from .base import DatabaseBaseModel as BaseModel

class Project(BaseModel):
    id: int = Field(title='Project inner id')
    name: str = Field(title='Project name')
    owner_id: int = Field(None, title='Project owner id')
    owner: str | None = Field(title='Project owner')
    admin_bot_id: int = Field(title='Project administrator bot id')
    tariff_id: int = Field(title='Project tariff id')
    payment_destination: str = Field(title='Project payment destination')
    payment_system_id: int = Field(title='Project payment system id')
