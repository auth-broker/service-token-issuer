"""User-related API routes."""

from typing import Annotated

from ab_core.cache.caches.base import CacheAsyncSession
from ab_core.cache.session_context import cache_session_async
from fastapi import APIRouter
from fastapi import Depends as FDepends
from fastapi.responses import StreamingResponse

from ab_service.token_issuer.schema.run import AuthenticateRequestAnnotated, RefreshRequestAnnotated
from ab_service.token_issuer.utils import sse_lines_from_models_async

router = APIRouter(prefix="/run", tags=["Run"])


@router.post(
    "/authenticate",
    response_class=StreamingResponse,
    responses={
        200: {
            "description": "Server-Sent Events stream",
            "content": {"text/event-stream": {"schema": {"type": "string"}}},
        }
    },
)
async def authenticate(
    request: AuthenticateRequestAnnotated,
    cache_session: Annotated[CacheAsyncSession, FDepends(cache_session_async)],
):
    """Run an auth flow and stream BaseModel events as Server-Sent Events.
    `request.authenticate(...)` returns a *sync* generator yielding BaseModels.
    """
    auth_flow = request.token_issuer.authenticate_async(cache_session=cache_session)

    return StreamingResponse(
        sse_lines_from_models_async(
            auth_flow,
            expose_secrets=True,
        ),
        media_type="text/event-stream",
        headers={
            # Helpful for proxies/browsers
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@router.post(
    "/refresh",
    response_class=StreamingResponse,
    responses={
        200: {
            "description": "Server-Sent Events stream",
            "content": {"text/event-stream": {"schema": {"type": "string"}}},
        }
    },
)
async def refresh(
    request: RefreshRequestAnnotated,
    cache_session: Annotated[CacheAsyncSession, FDepends(cache_session_async)],
):
    """Refresh your token using the token issuer."""
    auth_flow = request.token_issuer.refresh_async(
        request=request.refresh_token,
        cache_session=cache_session,
    )

    return StreamingResponse(
        sse_lines_from_models_async(
            auth_flow,
            expose_secrets=True,
        ),
        media_type="text/event-stream",
        headers={
            # Helpful for proxies/browsers
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
