###Takvim
##Fullcalenderdan start vs çekilicek
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Query
from app.schemas import CalendarEvent
from app.services import build_calendar_events

router = APIRouter(prefix="/calendar", tags=["calendar"])

@router.get("/events", response_model=list[CalendarEvent])
def calendar_events(
    start: datetime = Query(..., description="Takvim başlangıç tarihi."),
    end: datetime = Query(..., description="Takvim bitiş tarihi."),
    type: Optional[str] = Query(default=None, description="sales_delivery, purchase_arrival, stock_alert"),
    status: Optional[str] = Query(default=None)
):
    return build_calendar_events(start=start, end=end, event_type=type, status=status)