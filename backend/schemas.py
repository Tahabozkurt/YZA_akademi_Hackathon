from datetime import datetime,date
from typing import Any, Literal, Optional,Union
from pydantic import BaseModel



class CalendarEvent(BaseModel):
    id: str
    title: str
    start: Union[datetime, date, str]
    end: Optional[Union[datetime, date, str]] = None
    allDay: bool = True
    color: str
    extendedProps: dict[str, Any] = {}

###Dashboard'un frontend kısmındaki değerler
class DashboardSummary(BaseModel):
    pending_sales_orders: int
    delayed_sales_orders: int
    incoming_purchase_orders: int
    delayed_shipments: int
    low_stock_products: int

class StatusUpdate(BaseModel):
    status: str