from datetime import datetime

from pydantic import Field

from .base import DatabaseBaseModel as BaseModel
from .channel import Channel
from .user import UserProfile


class Payment(BaseModel):
    id: int = Field(title='User profile inner Id')
    external_id: str = Field(title='External ID')
    status: str = Field(title='Payment status')
    user: UserProfile = Field(title='User Profile')
    channel: Channel = Field(title='Channel')
    created_at: datetime = Field(title='Inserted at')
    updated_at: datetime = Field(title='Updated at')
