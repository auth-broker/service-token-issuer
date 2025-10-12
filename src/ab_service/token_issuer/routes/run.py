"""User-related API routes."""

from fastapi import APIRouter

router = APIRouter(prefix="/run", tags=["Run"])


@router.post("")
async def run():
    """Run an auth flow."""
    raise NotImplementedError()
