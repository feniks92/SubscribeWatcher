from fastapi import APIRouter, Body, Depends
from starlette.responses import JSONResponse

from libs.config import SUB_APP_CONFIG

from ...dependencies import basic_auth_security
from ...fast_api import fast_api_fabric
from .models import TraceRequest
from .trace_handler import MemoryTrace


def add_memory_trace_app(router=None):
    SUB_APP_CONFIG.APP_NAME = 'subscribe_watcher_profiling'

    sub_app = fast_api_fabric(config=SUB_APP_CONFIG)

    if not router:
        router = APIRouter(
            prefix="/profiling",
            responses={404: {"description": "Not found"}, },
            tags=['profiling', ],
            dependencies=[basic_auth_security, ]
        )

    router.add_api_route(
        path="/start",
        methods=["POST"],
        endpoint=start_trace
    )
    router.add_api_route(
        path="/state",
        methods=["POST"],
        endpoint=state_trace
    )
    router.add_api_route(
        path="/take_snapshot",
        methods=["POST"],
        endpoint=take_snapshot_route
    )
    router.add_api_route(
        path="/stop_trace",
        methods=["POST"],
        endpoint=stop_trace
    )
    sub_app.include_router(router)
    return sub_app


async def start_trace(trace: MemoryTrace = Depends(MemoryTrace)):
    if not trace.is_tracing():
        trace.start()
    return JSONResponse(content='Trace started')


async def state_trace(trace: MemoryTrace = Depends(MemoryTrace)):
    trace.is_tracing()
    return JSONResponse(content={'trace': trace.is_tracing()})


async def take_snapshot_route(body: TraceRequest = Body(example=TraceRequest(root=True,
                                                                             trace_time=1,
                                                                             limit=5,
                                                                             exclude_filters=['*env*',
                                                                                              '*frozen*',
                                                                                              '*string*'], )),
                              trace: MemoryTrace = Depends(MemoryTrace)):
    if not trace.is_tracing():
        return JSONResponse(status_code=400, content='The trace must be started')

    trace(root=body.root,
          limit=body.limit,
          exclude_filters=body.exclude_filters,
          include_filters=body.include_filters,
          ).take_snapshot()
    return JSONResponse(content=trace.result)


async def stop_trace(trace: MemoryTrace = Depends(MemoryTrace)):
    if trace.is_tracing():
        trace.stop()
    return JSONResponse(content='Trace stopped')
