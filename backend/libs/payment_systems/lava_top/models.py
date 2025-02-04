from enum import StrEnum
from typing import Optional, List

from pydantic import BaseModel, Field


class Currency(StrEnum):
    RUB = 'RUB'
    USD = 'USD'
    EUR = 'EUR'

class Periodicity(StrEnum):
    ONE_TIME = 'ONE_TIME'
    MONTHLY = 'MONTHLY'
    PERIOD_90_DAYS = 'PERIOD_90_DAYS'
    PERIOD_180_DAYS = 'PERIOD_180_DAYS'
    PERIOD_YEAR = 'PERIOD_YEAR'


class Price(BaseModel):
    amount: float = Field(..., gt=0)
    currency: Currency = Field(Currency.RUB)
    periodicity: Optional[Periodicity] = Field(Periodicity.ONE_TIME)


class Offer(BaseModel):
    id: str = Field(...)
    name: str = Field(...)
    description: Optional[str] = Field('')
    prices: List[Price] = Field(...)


class LavaTopItemData(BaseModel):
    _id: str = Field(..., alias='id')
    title: str = Field(...)
    description: Optional[str] = Field('')
    _type: Optional[str] = Field('', alias="type")
    offers: List[Offer] = Field(default_factory=list)

class LavaTopItem(BaseModel):
    _type: str = Field(..., alias='type')
    data: Offer = Field(default_factory=list)


class LavaTopProductsResponse(BaseModel):
    items: Optional[List[LavaTopItem]] = Field(default_factory=list)


class Invoice(BaseModel):
    _id: str = Field(..., alias='id')
    payment_url: str = Field(..., alias='paymentUrl')
