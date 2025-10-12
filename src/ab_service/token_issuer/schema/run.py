from typing import Annotated

from ab_core.auth_client.oauth2.schema.refresh import RefreshTokenRequest
from ab_core.token_issuer.token_issuers import TokenIssuer
from fastapi import Body
from pydantic import BaseModel

EXAMPLE_REQUEST = {
    "token_issuer": {
        "oauth2_flow": {
            "idp_prefix": "https://wemoney.auth.ap-southeast-2.amazoncognito.com/oauth2/idpresponse",
            "timeout": 600000,
            "type": "IMPERSONATION",
            "impersonator": {
                "tool": "PLAYWRIGHT_CDP_BROWSERLESS",
                "cdp_endpoint": "wss://browserless.matthewcoulter.dev/?stealth=true&blockAds=true&ignoreHTTPSErrors=true&timezoneId=Australia/Sydney",
                "cdp_gui_service": {"base_url": "https://browserless-gui.matthewcoulter.dev/"},
                "browserless_service": {
                    "base_url": "https://browserless.matthewcoulter.dev/",
                },
            },
        },
        "oauth2_client": {
            "config": {
                "client_id": "247ffs2l6um22baifm5o7nhkgh",
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
}


class AuthenticateRequest(BaseModel):
    """Generate a token, using user provided token issuer."""

    token_issuer: TokenIssuer


AuthenticateRequestAnnotated = Annotated[AuthenticateRequest, Body(..., example=EXAMPLE_REQUEST)]


class RefreshRequest(BaseModel):
    """Refresh a token, using user provided token issuer."""

    refresh_token: RefreshTokenRequest
    token_issuer: TokenIssuer


RefreshRequestAnnotated = Annotated[RefreshRequest, Body(..., example=EXAMPLE_REQUEST)]
