# backend/routers/chart_commands.py
from fastapi import APIRouter, Query, Request
from typing import Optional
from services.command_bus import CommandBus

router = APIRouter(prefix="/api", tags=["chart-commands"])


def _bus(request: Request) -> CommandBus:
    return request.app.state.command_bus  # type: ignore[attr-defined]


@router.get("/chart-commands")
async def get_chart_commands(
    request: Request,
    session_id: Optional[str] = Query(default=None, alias="sessionId"),
    cursor: Optional[int] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
):
    channel = session_id or "global"
    items, new_cursor = _bus(request).fetch(channel, after_seq=cursor, limit=limit)
    return {"commands": [i.model_dump() for i in items], "cursor": new_cursor}
