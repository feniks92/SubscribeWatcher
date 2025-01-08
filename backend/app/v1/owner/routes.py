from fastapi import APIRouter, Depends
from starlette.background import BackgroundTasks
from starlette.requests import Request

from libs import logging
from libs.database.sql_alchemy import pass_db_session, Session
from libs.dependencies import ParticipantsInfo
from libs.web_service.middleware.headers_parser import get_request_id

from .handler import ProjectHandler, TariffHandler
from .schemas import ProjectListResponse, ProjectResponse, GigaTariffListResponse, TariffResponse, ProjectRequest

log = logging.getLogger('owner_handler')

router = APIRouter(
    prefix="/owner",
    responses={404: {"description": "Not found"},
               422: {"description": "Request validation error"}},
)


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
                               projects=await handler.handle(bg_tasks=background_tasks))


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

    result = await handler.handle_one(bg_tasks=background_tasks, project_id=project_id)

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


#  Add or update tariff for project
@router.post("/projects/{project_id}/tariff", response_model=TariffResponse)
async def owner_projects_tariffs(
        project_id: int,
        request: Request,
        background_tasks: BackgroundTasks,
        db_session: Session = Depends(pass_db_session),
        participants: ParticipantsInfo = Depends(ParticipantsInfo)
) -> TariffResponse:
    ...


@router.get("/projects/giga_tariffs", response_model=GigaTariffListResponse)
async def giga_tariffs_list(
        request: Request,
        background_tasks: BackgroundTasks,
        db_session: Session = Depends(pass_db_session),
        participants: ParticipantsInfo = Depends(ParticipantsInfo)
) -> GigaTariffListResponse:
    handler = TariffHandler(session=db_session, participants=participants)
    return GigaTariffListResponse(rqId=get_request_id(), tariffs=await handler.giga_tariffs(bg_tasks=background_tasks))
