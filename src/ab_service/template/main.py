"""Main application for the User Service."""

from contextlib import asynccontextmanager
from typing import Annotated

from ab_core.alembic_auto_migrate.service import AlembicAutoMigrate
from ab_core.database.databases import Database
from ab_core.dependency import Depends, inject
from ab_core.logging.config import LoggingConfig
from fastapi import FastAPI

from ab_service.template.routes.heartbeat import router as heartbeat_router


@inject
@asynccontextmanager
async def lifespan(
    _app: FastAPI,
    _db: Annotated[Database, Depends(Database, persist=True)],  # cold start load db into cache
    logging_config: Annotated[LoggingConfig, Depends(LoggingConfig, persist=True)],
    alembic_auto_migrate: Annotated[AlembicAutoMigrate, Depends(AlembicAutoMigrate, persist=True)],
):
    """Lifespan context manager to handle startup and shutdown events."""
    logging_config.apply()
    alembic_auto_migrate.run()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(heartbeat_router)
