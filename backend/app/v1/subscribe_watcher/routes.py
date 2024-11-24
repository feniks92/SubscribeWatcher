from fastapi import APIRouter, Depends

router = APIRouter(
    prefix="/subscribe",
    tags=["subscribe_watcher"],
    responses={422: {"description": "Request validation error"}},
)