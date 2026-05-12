###Takvim
##Fullcalenderdan start vs çekilicek

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.database import get_session
from app.schemas import CalendarEvent
from app.services import build_calendar_events

router = APIRouter(prefix="/calendar", tags=["calendar"])

##Tarihleri çek
@router.get("/events", response_model=list[CalendarEvent])
#belirli tarihler arasındaki satış, sevkiyat veya stok uyarılarını getiricek
def calendar_events(
    ##Fullcalender'dan çekiliyor.
    start: datetime = Query(..., description="Calendar range start. FullCalendar sends this automatically."),
    end: datetime = Query(..., description="Calendar range end. FullCalendar sends this automatically."),
    ## Etkinlikleri filtrelemek için
    type: Optional[str] = Query(default=None, description="sales_delivery, purchase_arrival, shipment_delivery, stock_alert"),
    #Etkinlik durumunun filtrelenmesi
    status: Optional[str] = Query(default=None),
    #Veri tabanı bağlantısı
    session: Session = Depends(get_session),
):
    ##Build_calender_events çağırdık
    return build_calendar_events(session=session, start=start, end=end, event_type=type, status=status)
