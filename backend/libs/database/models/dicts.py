from pydantic import Field

from .base import DatabaseBaseModel as BaseModel


class BaseDictionaryModel(BaseModel):
    id: int = Field(title="Id")
    name: str = Field(title="Name")
    description: str = Field(title="Description")


class PaymentSystem(BaseDictionaryModel):
    active: bool = Field(title="Active")


class GigaTariff(BaseDictionaryModel):
    active: bool = Field(title="Active")
    tariff_fee: float = Field(title="Fee")
