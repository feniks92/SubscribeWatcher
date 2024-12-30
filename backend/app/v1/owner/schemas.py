from typing import Optional
from pydantic import BaseModel, Field

from app.v1.general.schemas import Tariff

from libs.authorize.schemas import AuthorizeItem


class ProjectItem(BaseModel):
    admin_bot_id: int = Field(..., alias='admin_bot_id')
    name: str = Field(..., alias='name')
    tariffs: list[Tariff] = Field(..., alias='tariff')


class ProjectResponse(AuthorizeItem, ProjectItem):
    rq_id: Optional[str] = Field(None, description='Идентификатор запроса',
                                 examples=['698c6fc1-b284-4f4b-b9a6-f317b1bf0811'], alias='rqId')


class ProjectListResponse(AuthorizeItem):
    rq_id: Optional[str] = Field(None, description='Идентификатор запроса',
                                 examples=['698c6fc1-b284-4f4b-b9a6-f317b1bf0811'], alias='rqId')
    projects: list[ProjectItem] = Field(..., alias='projects')


class TariffResponse(AuthorizeItem, Tariff):
    rq_id: Optional[str] = Field(None, description='Идентификатор запроса',
                                 examples=['698c6fc1-b284-4f4b-b9a6-f317b1bf0811'], alias='rqId')
