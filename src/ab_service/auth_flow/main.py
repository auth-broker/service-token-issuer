"""Main application for the User Service."""

from contextlib import asynccontextmanager
from typing import Annotated

from ab_core.dependency import Depends, inject
from ab_core.logging.config import LoggingConfig
from fastapi import FastAPI

from ab_service.auth_flow.routes.run import router as run_router


@inject
@asynccontextmanager
async def lifespan(
    _app: FastAPI,
    logging_config: Annotated[LoggingConfig, Depends(LoggingConfig, persist=True)],
):
    """Lifespan context manager to handle startup and shutdown events."""
    logging_config.apply()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(run_router)
