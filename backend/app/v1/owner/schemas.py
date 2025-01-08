from dataclasses import dataclass, asdict
from typing import Optional

from fastapi import Body
from pydantic import BaseModel, Field

from app.v1.general.schemas import TariffItem, GigaTariffItem

from libs.authorize.schemas import AuthorizeItem


class ProjectItem(BaseModel):
    id: int = Field(...)
    admin_bot_id: int = Field(..., alias='admin_bot_id')
    name: str = Field(..., alias='name')
    tariffs: Optional[list[TariffItem]] = Field(default_factory=list, alias='tariff')


class ProjectResponse(AuthorizeItem, ProjectItem):
    rq_id: Optional[str] = Field(None, description='Идентификатор запроса',
                                 examples=['698c6fc1-b284-4f4b-b9a6-f317b1bf0811'], alias='rqId')


class ProjectListResponse(AuthorizeItem):
    rq_id: Optional[str] = Field(None, description='Идентификатор запроса',
                                 examples=['698c6fc1-b284-4f4b-b9a6-f317b1bf0811'], alias='rqId')
    projects: list[ProjectItem] = Field(..., alias='projects')


class TariffResponse(AuthorizeItem, TariffItem):
    rq_id: Optional[str] = Field(None, description='Идентификатор запроса',
                                 examples=['698c6fc1-b284-4f4b-b9a6-f317b1bf0811'], alias='rqId')


class TariffListResponse(AuthorizeItem):
    rq_id: Optional[str] = Field(None, description='Идентификатор запроса',
                                 examples=['698c6fc1-b284-4f4b-b9a6-f317b1bf0811'], alias='rqId')
    tariffs: Optional[list[TariffItem]] = Field(default_factory=list, alias='tariffs')


@dataclass
class ProjectRequest:
    name: str = Body(..., alias='name')
    payment_system_id: int = Body(..., alias='payment_system_id')
    tariff_id: int = Body(..., alias='tariff_id')
    admin_bot_id: Optional[int] = Body(None, alias='admin_bot_id')
    payment_destination: Optional[str] = Body(None, alias='payment_destination')


class GigaTariffListResponse(AuthorizeItem):
    rq_id: Optional[str] = Field(None, description='Идентификатор запроса',
                                 examples=['698c6fc1-b284-4f4b-b9a6-f317b1bf0811'], alias='rqId')
    tariffs: list[GigaTariffItem] = Field(default_factory=list, alias='tariff')


@dataclass
class TariffRequest:
    name: str = Body(..., alias='name')
    description: str = Body(..., alias='description')
    payment_amount: int = Body(..., alias='paymentAmount')
    subscribe_duration: int = Body(..., alias='subscribeDuration', description='Subscribe Duration in months')

    dict = asdict


@dataclass
class TariffListRequest:
    tariffs: list[TariffRequest] = Body(..., alias='tariffs')
