"""Main application for the User Service."""

import asyncio
import sys

# Switch to Proactor (supports subprocess) for Playwright async driver
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from contextlib import asynccontextmanager
from typing import Annotated

from ab_core.cache.caches import Cache
from ab_core.dependency import Depends, inject
from ab_core.logging.config import LoggingConfig
from fastapi import FastAPI
from playwright.async_api import async_playwright

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
    if sys.platform == "win32":
        try:
            async with async_playwright() as p:
                _ = p.chromium
        except Exception as e:
            raise RuntimeError(
                "Sorry, windows doesn't support async playwright. Please run this in docker or wsl instead."
            ) from e
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(run_router)
