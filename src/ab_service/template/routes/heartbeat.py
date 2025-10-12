"""User-related API routes."""

from typing import Annotated
from fastapi import APIRouter
from fastapi import Depends as FDepends

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ab_core.database.session_context import db_session_async
from ab_service.template.models.heartbeat import Heartbeat

router = APIRouter(prefix="/heartbeat", tags=["Heartbeat"])


@router.get("", response_model=list[Heartbeat])
async def heartbeat(
    db_session: Annotated[AsyncSession, FDepends(db_session_async)],
):
    """Insert a heartbeat row and return it."""
    hb = Heartbeat()  # last_seen auto-filled (UTC)

    db_session.add(hb)
    await db_session.flush()

    result = await db_session.execute(select(Heartbeat).order_by(Heartbeat.id))
    heartbeats = result.scalars().all()
    return heartbeats
