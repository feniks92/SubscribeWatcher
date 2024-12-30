from fastapi import APIRouter, Depends
from starlette.background import BackgroundTasks
from starlette.requests import Request

from libs import logging
from libs.database.sql_alchemy import pass_db_session, Session
from libs.dependencies import ParticipantsInfo

from .handler import ProjectHandler, SubscriptionHandler
from .schemas import ProjectResponse, SubscriptionInfoResponse

log = logging.getLogger('watcher_handler')

router = APIRouter(
    prefix="/subscribe",
    responses={404: {"description": "Not found"},
               422: {"description": "Request validation error"}},
)


@router.get("/tariffs", response_model=TariffsInfoResponse)
async def tariffs_list(
        request: Request,
        background_tasks: BackgroundTasks,
        project_info: TariffRequest,
        db_session: Session = Depends(pass_db_session),
        participants: ParticipantsInfo = Depends(ParticipantsInfo), ) -> TariffsInfoResponse:
    ...


# Ручка для получения текущих подписок пользователя
@router.get("/subscription", response_model=SubscriptionInfoResponse)
async def subscription_info(
        request: Request,
        background_tasks: BackgroundTasks,
        db_session: Session = Depends(pass_db_session),
        participants: ParticipantsInfo = Depends(ParticipantsInfo),
) -> SubscriptionInfoResponse:
    handler = SubscriptionHandler(session=db_session,
                                  participants=participants)

    return await handler.handle(bg_tasks=background_tasks)
