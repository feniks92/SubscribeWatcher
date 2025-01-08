from pydantic import Field

from .base import DatabaseBaseModel as BaseModel


class TariffModel(BaseModel):
    id: int = Field(title="Id")
    name: str = Field(title="Name")
    description: str = Field(title="Description")
    active: bool = Field(title="Active")
    project_id: int = Field(title="Project ID")
    payment_amount: int = Field(title="Payment Amount")
    subscribe_duration: int = Field(title="Subscribe Duration in months")