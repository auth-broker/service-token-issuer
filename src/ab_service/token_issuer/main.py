"""Main application for the User Service."""

import asyncio
import sys

if sys.platform.startswith("win"):
    # this is necessary to fix an issue with playwright managing its own event loop
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
from contextlib import asynccontextmanager
from typing import Annotated

from ab_core.cache.caches import Cache
from ab_core.dependency import Depends, inject
from ab_core.logging.config import LoggingConfig
from fastapi import FastAPI

from ab_service.token_issuer.routes.run import router as run_router


@inject
@asynccontextmanager
async def lifespan(
    _app: FastAPI,
    _cache: Annotated[Cache, Depends(Cache, persist=True)],
    logging_config: Annotated[LoggingConfig, Depends(LoggingConfig, persist=True)],
):
    """Lifespan context manager to handle startup and shutdown events."""
    logging_config.apply()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(run_router)
