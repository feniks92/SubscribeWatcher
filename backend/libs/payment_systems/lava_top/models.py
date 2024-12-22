from typing import Optional, List

from pydantic import BaseModel, Field


class Offer(BaseModel):
    id: str = Field(...)


class LavaTopItem(BaseModel):
    title: str = Field(...)
    offers: List[Offer] = Field(default_factory=list)


class LavaTopProductsResponse(BaseModel):
    items: Optional[List[LavaTopItem]] = Field(default_factory=list)


class Invoice(BaseModel):
    id: str = Field(...)
    payment_url: str = Field(..., alias='paymentUrl')
