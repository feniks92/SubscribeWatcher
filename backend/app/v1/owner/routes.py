from fastapi import APIRouter, Depends
from starlette.background import BackgroundTasks
from starlette.requests import Request

from libs import logging
from libs.database.sql_alchemy import pass_db_session, Session
from libs.dependencies import ParticipantsInfo
from libs.web_service.middleware.headers_parser import get_request_id

from .handler import ProjectHandler, TariffHandler
from .schemas import (ProjectListResponse, ProjectResponse, GigaTariffListResponse, TariffResponse,
                      ProjectRequest, TariffListRequest, TariffListResponse)

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
        меняем тариф (POST /projects/{project_id}/tariff)
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
        background_tasks: BackgroundTasks,
        db_session: Session = Depends(pass_db_session),
        participants: ParticipantsInfo = Depends(ParticipantsInfo)
) -> ProjectResponse:
    ...


#  Add tariffs for project
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


@router.get("/projects/giga_tariffs", response_model=GigaTariffListResponse)
async def giga_tariffs_list(
        request: Request,
        background_tasks: BackgroundTasks,
        db_session: Session = Depends(pass_db_session),
        participants: ParticipantsInfo = Depends(ParticipantsInfo)
) -> GigaTariffListResponse:
    handler = TariffHandler(session=db_session, participants=participants)
    return GigaTariffListResponse(rqId=get_request_id(), tariffs=await handler.giga_tariffs(bg_tasks=background_tasks))
