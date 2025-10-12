"""Main application for the User Service."""

import sys, asyncio

# async playwright + windows with python 3.13 has some issues
# just use docker, its a lot easier
if sys.platform == "win32":
    # Switch to Proactor (supports subprocess) for Playwright async driver
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from playwright.async_api import async_playwright
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
    # validate playwright installation (windows)
    if sys.platform == "win32":
        async with async_playwright() as p:
            _ = p.chromium
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(run_router)
