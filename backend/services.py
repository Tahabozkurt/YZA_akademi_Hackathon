from datetime import datetime, timezone
from typing import Optional
# Yollar backend olarak düzeltildi
from backend.database import supabase
from backend.schemas import CalendarEvent

COLORS = {
    "sales_delivery": "#2563eb",
    "purchase_arrival": "#16a34a",
    "delayed": "#ef4444",
}

def ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)

def build_calendar_events(
    start: datetime, end: datetime,
    event_type: Optional[str] = None,
    status: Optional[str] = None,
    user_id: Optional[str] = None # SAAS GÜVENLİĞİ
) -> list[CalendarEvent]:
    events: list[CalendarEvent] = []
    now = datetime.now(timezone.utc)
    start = ensure_utc(start)
    end = ensure_utc(end)
    is_all = event_type in (None, "", "all", "Tümü")

    # 1. SİPARİŞ TESLİMATLARI
    if is_all or event_type == "sales_delivery":
        query = supabase.table("orders").select("*").gte("estimated_delivery", start.strftime("%Y-%m-%d")).lte("estimated_delivery", end.strftime("%Y-%m-%d"))
        if status: query = query.eq("status", status)
        if user_id: query = query.eq("user_id", user_id)

        for order in (query.execute().data or []):
            delivery_date = order.get("estimated_delivery")
            if not delivery_date: continue
            order_status = order.get("status", "")
            is_delayed = order_status == "Gecikmiş" or (delivery_date < now.strftime("%Y-%m-%d") and order_status not in ["Teslim Edildi", "İptal Edildi"])

            events.append(CalendarEvent(
                id=f"sales-{order['id']}",
                title=f"📦 {order.get('customer_name', '')} - #{order.get('order_number', order['id'])}",
                start=delivery_date,
                allDay=True,
                color=COLORS["delayed"] if is_delayed else COLORS["sales_delivery"],
                extendedProps={
                    "type": "sales_delivery",
                    "display_status": order_status,
                    "is_delayed": is_delayed,
                    "delay_text": "⚠️ Gecikme Mevcut" if is_delayed else "✅ Zamanında",
                    "quantity": f"{order.get('quantity', '-')} Adet",
                    "tracking_link": order.get("tracking_link")
                }
            ))

    # 2. TEDARİK GELİŞLERİ
    if is_all or event_type == "purchase_arrival":
        query = supabase.table("deliveries").select("*").gte("date", start.strftime("%Y-%m-%d")).lte("date", end.strftime("%Y-%m-%d"))
        if status: query = query.eq("status", status)
        if user_id: query = query.eq("user_id", user_id)

        for delivery in (query.execute().data or []):
            delivery_date = delivery.get("date")
            if not delivery_date: continue
            delivery_status = delivery.get("status", "")
            is_delayed = delivery_status == "Gecikmiş" or (delivery_date < now.strftime("%Y-%m-%d") and delivery_status not in ["Tamamlandı", "İptal Edildi"])

            events.append(CalendarEvent(
                id=f"delivery-{delivery['id']}",
                title=f"🚚 {delivery.get('supplier') or 'Tedarikçi'} - #{delivery['id']}",
                start=delivery_date,
                allDay=True,
                color=COLORS["delayed"] if is_delayed else COLORS["purchase_arrival"],
                extendedProps={
                    "type": "purchase_arrival",
                    "display_status": delivery_status,
                    "is_delayed": is_delayed,
                    "delay_text": "⚠️ Gecikme" if is_delayed else "✅ Bekleniyor",
                    "quantity": f"{delivery.get('quantity', '-')} Adet"
                }
            ))

    return sorted(events, key=lambda e: str(e.start))