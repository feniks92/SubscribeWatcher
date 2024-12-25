from datetime import datetime

from pydantic import Field

from .base import DatabaseBaseModel as BaseModel
from .project import Project
from .user import UserProfile
from .tariff import TariffModel


class Payment(BaseModel):
    id: int = Field(title='User profile inner Id')
    external_id: str = Field(title='External ID')
    status: str = Field(title='Payment status')
    user: UserProfile = Field(title='User Profile')
    project: Project = Field(title='Project')
    created_at: datetime = Field(title='Inserted at')
    updated_at: datetime = Field(title='Updated at')
    tariff: TariffModel = Field(title='Tariff')
