from pydantic import Field

from .base import DatabaseBaseModel as BaseModel

class Channel(BaseModel):
    telegram_id: str = Field(title='Channel telegram id')
    id: int = Field(title='Channel inner id')
    name: str = Field(title='Channel name')
    owner_id: int = Field(None, title='Channel owner id')
    owner: str | None = Field(title='Channel owner')
    admin_bot_id: int = Field(title='Channel administrator bot id')
    tariff_id: int = Field(title='Channel tariff id')
    payment_amount: int = Field(title='Channel payment amount')
    payment_destination: str = Field(title='Channel payment destination')
    payment_system_id: int = Field(title='Channel payment system id')
