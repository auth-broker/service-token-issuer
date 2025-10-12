"""User-related API routes."""

from collections.abc import Iterator
from typing import Annotated

from ab_core.cache.caches.base import CacheSession
from ab_core.cache.session_context import cache_session_sync
from ab_core.token_issuer.token_issuers import TokenIssuer
from fastapi import APIRouter, Body
from fastapi import Depends as FDepends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from ab_service.token_issuer.utils import sse_lines_from_models

router = APIRouter(prefix="/run", tags=["Run"])

EXAMPLE_REQUEST = {
    "oauth2_flow": {
        "idp_prefix": "https://wemoney.auth.ap-southeast-2.amazoncognito.com/oauth2/idpresponse",
        "timeout": 9999999,
        "type": "IMPERSONATION",
        "impersonator": {
            "tool": "PLAYWRIGHT_CDP_BROWSERLESS",
            "cdp_endpoint": "wss://browserless.matthewcoulter.dev/?stealth=true&blockAds=true&ignoreHTTPSErrors=true&timezoneId=Australia/Sydney",
            "cdp_headers": None,
            "cdp_timeout": None,
            "cdp_gui_service": {"base_url": "https://browserless-gui.matthewcoulter.dev/"},
            "browserless_service": {
                "base_url": "https://browserless.matthewcoulter.dev/",
                "sessions_url": "https://browserless.matthewcoulter.dev//sessions",
                "ws_url_prefix": "wss://browserless.matthewcoulter.dev",
            },
        },
    },
    "oauth2_client": {
        "config": {
            "client_id": "247ffs2l6um22baifm5o7nhkgh",
            "client_secret": None,
            "redirect_uri": "https://app.wemoney.com.au/oauth_redirect",
            "authorize_url": "https://wemoney.auth.ap-southeast-2.amazoncognito.com/oauth2/authorize",
            "token_url": "https://wemoney.auth.ap-southeast-2.amazoncognito.com/oauth2/token",
        },
        "type": "PKCE",
    },
    "identity_provider": "Google",
    "response_type": "code",
    "scope": "openid email profile",
    "type": "PKCE",
}


@router.post("/authenticate")
async def authenticate(
    request: Annotated[TokenIssuer, Body(..., example=EXAMPLE_REQUEST)],
    cache_session: Annotated["CacheSession", FDepends(cache_session_sync)],
):
    """Run an auth flow and stream BaseModel events as Server-Sent Events.
    `request.authenticate(...)` returns a *sync* generator yielding BaseModels.
    """
    auth_flow = request.authenticate(cache_session=cache_session)

    return StreamingResponse(
        sse_lines_from_models(auth_flow),
        media_type="text/event-stream",
        headers={
            # Helpful for proxies/browsers
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
