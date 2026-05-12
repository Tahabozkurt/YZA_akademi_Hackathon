##Özetlerin Yer Aldığı Dashboard
##
##Tarih vs
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends

from sqlmodel import Session, func, select
from app.database import get_session
from app.models import Product, PurchaseOrder, SalesOrder, Shipment
from app.schemas import DashboardSummary

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/summary", response_model=DashboardSummary)
def dashboard_summary(session: Session = Depends(get_session)):
    ##Mevcut zamanı çek +7 gün ekle
    now = datetime.utcnow()
    next_week = now + timedelta(days=14)

    ##Veri tabanından verileri çekme kısmı
    ##Bekleyensatışlar
    pending_sales = session.exec(select(func.count(SalesOrder.id)).where(SalesOrder.status.in_(["pending", "preparing", "shipped"]))).one()
    ###Gecikmiş satışlar
    delayed_sales = session.exec(select(func.count(SalesOrder.id)).where((SalesOrder.status == "delayed") | (SalesOrder.promised_delivery_at < now))).one()
    ##Gelen alımlar
    incoming_po = session.exec(select(func.count(PurchaseOrder.id)).where(PurchaseOrder.expected_arrival_at <= next_week, PurchaseOrder.status.in_(["planned", "ordered", "in_transit"]))).one()
    ##Gecikmiş sevkiyatlar
    delayed_shipments = session.exec(select(func.count(Shipment.id)).where((Shipment.status == "delayed") | (Shipment.estimated_delivery_at < now))).one()
    ###Kritik stok uyarısı
    low_stock = session.exec(select(func.count(Product.id)).where(Product.stock_quantity <= Product.reorder_threshold)).one()
    return DashboardSummary(
        pending_sales_orders=pending_sales,
        delayed_sales_orders=delayed_sales,
        incoming_purchase_orders=incoming_po,
        delayed_shipments=delayed_shipments,
        low_stock_products=low_stock,
    )
##return olarak bunlar dönmüş olucak