from datetime import datetime, timedelta, timezone
from typing import Optional
from sqlmodel import Session, select
from app.models import (
    Product, PurchaseOrder, PurchaseStatus,
    SalesOrder, OrderStatus, Shipment, ShipmentStatus
)
from app.schemas import CalendarEvent
STATUS_TR = {
    "pending": "Beklemede",
    "preparing": "Hazırlanıyor",
    "shipped": "Kargoya Verildi",
    "delivered": "Teslim Edildi",
    "delayed": "Gecikmiş",
    "cancelled": "İptal Edildi",
    "planned": "Planlandı",
    "ordered": "Sipariş Verildi",
    "in_transit": "Yolda/Taşımada",
    "label_created": "Etiket Oluşturuldu"
}

TYPE_TR = {
    "sales_delivery": "Satış Teslimatı",
    "purchase_arrival": "Tedarik Gelişi",
    "shipment_delivery": "Kargo Teslimatı",
    "stock_alert": "Kritik Stok Uyarısı"
}
COLORS = {
    "sales_delivery": "#2563eb",
    "purchase_arrival": "#16a34a",
    "shipment_delivery": "#9333ea",
    "stock_alert": "#dc2626",
    "delayed": "#ef4444",
}


def ensure_utc(value: datetime) -> datetime:
    """Zaman damgasını UTC olarak mühürler."""
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def parse_order_status(status: Optional[str]) -> Optional[OrderStatus]:
    if not status: return None
    try:
        return OrderStatus(status)
    except ValueError:
        return None


def build_calendar_events(
        session: Session, start: datetime, end: datetime,
        event_type: Optional[str] = None, status: Optional[str] = None
) -> list[CalendarEvent]:
    events: list[CalendarEvent] = []
    now = datetime.now(timezone.utc)
    start = ensure_utc(start)
    end = ensure_utc(end)

##Hepsini getirmesi için ekrana
    is_all = event_type in (None, "", "all", "Tümü")

# 1. SATIŞ TESLİMATLARI
    if is_all or event_type == "sales_delivery":
        stmt = select(SalesOrder).where(
            SalesOrder.promised_delivery_at >= start,
            SalesOrder.promised_delivery_at <= end
        )

        should_query = True
        if status:
            try:
                # Durum bu tabloya ait değilse ValueError fırlatır
                stmt = stmt.where(SalesOrder.status == OrderStatus(status))
            except ValueError:
                should_query = False

        if should_query:
            for order in session.exec(stmt).all():
                promised_at = ensure_utc(order.promised_delivery_at)
                is_delayed = order.status == OrderStatus.delayed or (
                        promised_at < now and order.status not in [OrderStatus.delivered, OrderStatus.cancelled]
                )
                color = COLORS["delayed"] if is_delayed else COLORS["sales_delivery"]
                events.append(CalendarEvent(
                    id=f"sales-{order.id}",
                    title=f"📦 Satış: #{order.id} - {order.customer_name}",
                    start=promised_at,
                    end=promised_at + timedelta(hours=1),
                    color=color,
                    extendedProps={
                        "display_status": STATUS_TR.get(order.status.value, order.status.value),
                        "customer": order.customer_name,
                        "is_delayed": is_delayed,
                        "delay_text": "⚠️ Gecikme Mevcut" if is_delayed else "✅ Zamanında",
                        "quantity": f"{order.quantity} Adet"
                    }
                ))

        # 2. TEDARİK GELİŞLERİ
    if is_all or event_type == "purchase_arrival":
        stmt = select(PurchaseOrder).where(
            PurchaseOrder.expected_arrival_at >= start,
            PurchaseOrder.expected_arrival_at <= end
        )

        should_query = True
        if status:
            try:
                stmt = stmt.where(PurchaseOrder.status == PurchaseStatus(status))
            except ValueError:
                should_query = False

        if should_query:
            for po in session.exec(stmt).all():
                arrival_at = ensure_utc(po.expected_arrival_at)
                is_delayed = po.status == PurchaseStatus.delayed or (
                        arrival_at < now and po.status not in [PurchaseStatus.arrived, PurchaseStatus.cancelled]
                )
                color = COLORS["delayed"] if is_delayed else COLORS["purchase_arrival"]
                events.append(CalendarEvent(
                    id=f"purchase-{po.id}",
                    title=f"🚚 Tedarik: PO #{po.id} | {po.supplier_name}",
                    start=arrival_at,
                    end=arrival_at + timedelta(hours=1),
                    color=color,
                    extendedProps={
                        "display_status": STATUS_TR.get(po.status.value, po.status.value),
                        "is_delayed": is_delayed,
                        "delay_text": "⚠️ Gecikme" if is_delayed else "✅ Bekleniyor",
                        "quantity": f"{po.quantity} Adet"
                    }
                ))

        # 3. KARGO SEVKİYATLARI
    if is_all or event_type == "shipment_delivery":
        stmt = select(Shipment).where(
            Shipment.estimated_delivery_at >= start,
            Shipment.estimated_delivery_at <= end
        )

        should_query = True
        if status:
            try:
                stmt = stmt.where(Shipment.status == ShipmentStatus(status))
            except ValueError:
                should_query = False

        if should_query:
            for shipment in session.exec(stmt).all():
                delivery_at = ensure_utc(shipment.estimated_delivery_at)
                is_delayed = shipment.status == ShipmentStatus.delayed or (
                        delivery_at < now and shipment.status not in [ShipmentStatus.delivered, ShipmentStatus.failed]
                )
                color = COLORS["delayed"] if is_delayed else COLORS["shipment_delivery"]
                events.append(CalendarEvent(
                    id=f"shipment-{shipment.id}",
                    title=f"🚛 Kargo: Sipariş #{shipment.sales_order_id}",
                    start=delivery_at,
                    end=delivery_at + timedelta(hours=1),
                    color=color,
                    extendedProps={
                        "display_status": STATUS_TR.get(shipment.status.value, shipment.status.value),
                        "is_delayed": is_delayed,
                        "delay_text": "⚠️ Gecikme" if is_delayed else "✅ Yolda",
                        "carrier": shipment.carrier_name,
                        "tracking": shipment.tracking_code
                    }
                ))

        # 4. KRİTİK STOK UYARILARI
    if (is_all or event_type == "stock_alert") and start <= now <= end:
        stmt = select(Product).where(Product.stock_quantity <= Product.reorder_threshold)
        for product in session.exec(stmt).all():
            events.append(CalendarEvent(
                id=f"stock-{product.id}",
                title=f"⚠️ Kritik Stok: {product.name}",
                start=now,
                end=now + timedelta(hours=1),
                color=COLORS["stock_alert"],
                extendedProps={
                    "current_stock": f"{product.stock_quantity} birim kaldı",
                    "threshold": f"Kritik eşik: {product.reorder_threshold}"
                }
            ))

    return sorted(events, key=lambda event: event.start)