from datetime import datetime
from typing import Any, Literal, Optional
from pydantic import BaseModel

CalendarEventType = Literal["sales_delivery", "purchase_arrival", "shipment_delivery", "stock_alert"]


class CalendarEvent(BaseModel):
    id: str
    title: str
    start: datetime
    end: datetime##Zorunlu tuttuk
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