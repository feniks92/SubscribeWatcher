from fastapi import APIRouter, Depends
from starlette.background import BackgroundTasks
from starlette.requests import Request

from libs import logging
from libs.database.sql_alchemy import pass_db_session, Session
from libs.dependencies import ParticipantsInfo
from libs.shared import TariffListResponse
from libs.web_service.middleware.headers_parser import get_request_id

from .handler import SubscriptionHandler
from .schemas import SubscriptionInfoResponse, SubscriptionRenewRequest

log = logging.getLogger('watcher_handler')

router = APIRouter(
    prefix="/subscribe",
    responses={404: {"description": "Not found"},
               422: {"description": "Request validation error"}},
)


@router.get("/tariffs", response_model=TariffListResponse)
async def tariffs_list(
        request: Request,
        background_tasks: BackgroundTasks,
        db_session: Session = Depends(pass_db_session),
        participants: ParticipantsInfo = Depends(ParticipantsInfo)
) -> TariffListResponse:
    handler = SubscriptionHandler(session=db_session,
                                  participants=participants)

    return TariffListResponse(rqId=get_request_id(),
                              tariffs=await handler.get_tariff_list(
                                  bg_tasks=background_tasks))



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

    subscription = await handler.get_subscription_info(bg_tasks=background_tasks)

    return SubscriptionInfoResponse(rqId=get_request_id(),
                                    subscription=subscription)

@router.post("/subscription", response_model=SubscriptionInfoResponse)
async def create_renew_subscription(
        request: Request,
        request_data: SubscriptionRenewRequest,
        background_tasks: BackgroundTasks,
        db_session: Session = Depends(pass_db_session),
        participants: ParticipantsInfo = Depends(ParticipantsInfo)
) -> SubscriptionInfoResponse:
    ...