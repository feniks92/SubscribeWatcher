from fastapi import APIRouter, Depends
from starlette.background import BackgroundTasks
from starlette.requests import Request

from libs import logging
from libs.database.models import Project
from libs.database.sql_alchemy import pass_db_session, Session
from libs.dependencies import ParticipantsInfo
from libs.shared import TariffListResponse
from libs.payment_systems.lava_top.models import LavaTopProductsResponse
from libs.web_service.middleware.headers_parser import get_request_id

from .handler import ProjectHandler, TariffHandler
from .schemas import (ExternalProjectRequest, ProjectListResponse, ProjectResponse, GigaTariffListResponse,
                      TariffResponse, ProjectRequest, TariffListRequest, TariffRequest)

log = logging.getLogger('owner_handler')

router = APIRouter(
    prefix="/owner",
    responses={404: {"description": "Not found"},
               422: {"description": "Request validation error"}},
)

'''
Стандартный путь работы с проектом:
запрашиваем список проектов (GET /projects)
    Если нет проектов -> 
        Запрашивваем список доступных для проекта тарифов (GET /projects/giga_tariffs)
        создаем проект (POST /projects)
        создаем тарифы для уже для проекта, которые на месяц, 3 месяца, и т.д. (POST /projects/{project_id}/tariffs)
        
    Если проекты есть -> 
        получаем тарифы (GET /projects/{project_id}/tariffs)
        меняем тариф (POST /projects/{project_id}/tariff/{tariff_id})
        меняем проект (POST /projects/{project_id})
    
Дополнительно есть возможность получить инфу по конкретному проекту (GET /projects/{project_id}) 
'''


@router.get("/projects", response_model=ProjectListResponse)
async def owner_projects_list(
        request: Request,
        background_tasks: BackgroundTasks,
        db_session: Session = Depends(pass_db_session),
        participants: ParticipantsInfo = Depends(ParticipantsInfo),
) -> ProjectListResponse:
    handler = ProjectHandler(session=db_session,
                             participants=participants)

    return ProjectListResponse(rqId=get_request_id(),
                               projects=await handler.get_all(bg_tasks=background_tasks))


@router.post("/projects", response_model=ProjectResponse)
async def owner_project_create(
        request: Request,
        project_data: ProjectRequest,
        background_tasks: BackgroundTasks,
        db_session: Session = Depends(pass_db_session),
        participants: ParticipantsInfo = Depends(ParticipantsInfo),
) -> ProjectResponse:
    handler = ProjectHandler(session=db_session,
                             participants=participants)

    result = await handler.create(bg_tasks=background_tasks, project_data=project_data)

    return ProjectResponse(rqId=get_request_id(),
                           admin_bot_id=result.admin_bot_id,
                           name=result.name,
                           tariffs=result.tariffs,
                           )


@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def owner_projects_get(
        project_id: int,
        request: Request,
        background_tasks: BackgroundTasks,
        db_session: Session = Depends(pass_db_session),
        participants: ParticipantsInfo = Depends(ParticipantsInfo)
) -> ProjectResponse:
    handler = ProjectHandler(session=db_session,
                             participants=participants)

    result = await handler.get_one(bg_tasks=background_tasks, project_id=project_id)

    return ProjectResponse(
        rqId=get_request_id(),
        admin_bot_id=result.admin_bot_id,
        name=result.name,
        tariffs=result.tariffs,
    )


#  This for update project via id
@router.post("/projects/{project_id}", response_model=ProjectResponse)
async def owner_projects_update(
        project_id: int,
        request: Request,
        project_data: ProjectRequest,
        background_tasks: BackgroundTasks,
        db_session: Session = Depends(pass_db_session),
        participants: ParticipantsInfo = Depends(ParticipantsInfo)
) -> ProjectResponse:
    handler = ProjectHandler(session=db_session,
                             participants=participants)

    result = await handler.update(bg_tasks=background_tasks, project_id=project_id, project_data=project_data)

    return ProjectResponse(rqId=get_request_id(),
                           admin_bot_id=result.admin_bot_id,
                           name=result.name,
                           tariffs=result.tariffs,
                           )


# TODO чуть костыльный метод, используется пока для дозаполнения инфы, получаемой из внешних источников (лаватоп).
# Есть необходимость либо переделать его в вариант GraphQL, либо принимать аналог DTO, либо допилить
# схемы опциональными параметрами (GraphQL на минималках), тогда потребуется валидация связки параметров
@router.post("/projects/{project_id}/update", response_model=ProjectResponse)
async def owner_project_external_update(
        project_id: int,
        request: Request,
        external_project_data: ExternalProjectRequest,
        background_tasks: BackgroundTasks,
        db_session: Session = Depends(pass_db_session),
        participants: ParticipantsInfo = Depends(ParticipantsInfo)
) -> LavaTopProductsResponse:
    handler = ProjectHandler(session=db_session,
                             participants=participants)
    result = handler.update_by_external(bg_tasks=background_tasks, project_id=project_id, external_project_data=external_project_data)


# Add tariffs for project
@router.post("/projects/{project_id}/tariffs", response_model=TariffListResponse)
async def owner_projects_tariffs(
        project_id: int,
        request: Request,
        tariffs_list_data: TariffListRequest,
        background_tasks: BackgroundTasks,
        db_session: Session = Depends(pass_db_session),
        participants: ParticipantsInfo = Depends(ParticipantsInfo)
) -> TariffListResponse:
    handler = TariffHandler(session=db_session,
                            participants=participants)

    return TariffListResponse(rqId=get_request_id(),
                              tariffs=await handler.insert_tariffs(
                                  bg_tasks=background_tasks,
                                  tariffs_list_data=tariffs_list_data,
                                  project_id=project_id))


@router.post("/projects/{project_id}/tariff/{tariff_id}", response_model=TariffResponse)
async def owner_project_tariff_update(
        project_id: int,
        tariff_id: int,
        request: Request,
        tariff_data: TariffRequest,
        background_tasks: BackgroundTasks,
        db_session: Session = Depends(pass_db_session),
        participants: ParticipantsInfo = Depends(ParticipantsInfo)
) -> TariffResponse:
    handler = TariffHandler(session=db_session,
                            participants=participants)

    updated_tariff = await handler.update_tariff(bg_tasks=background_tasks, project_id=project_id,
                                                 tariff_id=tariff_id, tariff_data=tariff_data)

    return TariffResponse(rqId=get_request_id(),
                          **updated_tariff.as_dict())


@router.get("/projects/{project_id}/tariffs", response_model=TariffListResponse)
async def owner_projects_tariffs_get(
        project_id: int,
        request: Request,
        background_tasks: BackgroundTasks,
        db_session: Session = Depends(pass_db_session),
        participants: ParticipantsInfo = Depends(ParticipantsInfo)
) -> TariffListResponse:
    handler = TariffHandler(session=db_session,
                            participants=participants)

    return TariffListResponse(rqId=get_request_id(),
                              tariffs=await handler.get_tariffs(bg_tasks=background_tasks, project_id=project_id))


@router.get("/projects/giga_tariffs", response_model=GigaTariffListResponse)
async def giga_tariffs_list(
        request: Request,
        background_tasks: BackgroundTasks,
        db_session: Session = Depends(pass_db_session),
        participants: ParticipantsInfo = Depends(ParticipantsInfo)
) -> GigaTariffListResponse:
    handler = TariffHandler(session=db_session, participants=participants)
    return GigaTariffListResponse(rqId=get_request_id(), tariffs=await handler.giga_tariffs(bg_tasks=background_tasks))
