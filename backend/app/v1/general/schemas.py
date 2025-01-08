from typing import Optional

from pydantic import BaseModel, Field

from libs.authorize.schemas import AuthorizeItem


class AuthorizeResponse(AuthorizeItem):
    rq_id: Optional[str] = Field(None, description='Идентификатор запроса',
                                 examples=['698c6fc1-b284-4f4b-b9a6-f317b1bf0811'], alias='rqId')


class GigaTariffItem(BaseModel):
    id: int = Field(...)
    name: str = Field(..., alias='name')
    description: str = Field(..., alias='description')


class TariffItem(BaseModel):
    id: int = Field(...)
    name: str = Field(..., alias='name')
    description: str = Field(..., alias='description')
    payment_amount: int = Field(..., alias='paymentAmount')
    project_id: int = Field(..., alias='projectId')
    subscribe_duration: int = Field(..., alias='subscribeDuration', description='Subscribe Duration in months')
