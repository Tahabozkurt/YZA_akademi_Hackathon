from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Query
from backend.schemas import CalendarEvent
from backend.services import build_calendar_events

router = APIRouter(prefix="/calendar", tags=["calendar"])

@router.get("/events", response_model=list[CalendarEvent])
def calendar_events(
    start: datetime = Query(..., description="Takvim başlangıç tarihi."),
    end: datetime = Query(..., description="Takvim bitiş tarihi."),
    type: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    user_id: Optional[str] = Query(default=None)
):
    return build_calendar_events(start=start, end=end, event_type=type, status=status, user_id=user_id)