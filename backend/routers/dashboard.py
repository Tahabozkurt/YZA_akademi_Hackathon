from datetime import datetime, timedelta
from fastapi import APIRouter, Query
from backend.database import supabase
from backend.schemas import DashboardSummary

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/summary", response_model=DashboardSummary)
def dashboard_summary(user_id: str = Query(default=None)):
    now = datetime.utcnow()
    next_week = now + timedelta(days=14)

    pq = supabase.table("orders").select("id", count="exact").in_("status", ["Beklemede", "Hazırlanıyor", "Kargoya Verildi"])
    if user_id: pq = pq.eq("user_id", user_id)
    pending_sales = pq.execute().count or 0

    dq = supabase.table("orders").select("id", count="exact").eq("status", "Gecikmiş")
    if user_id: dq = dq.eq("user_id", user_id)
    delayed_sales = dq.execute().count or 0

    iq = supabase.table("deliveries").select("id", count="exact").lte("date", next_week.strftime("%Y-%m-%d")).gte("date", now.strftime("%Y-%m-%d")).in_("status", ["Planlandı"])
    if user_id: iq = iq.eq("user_id", user_id)
    incoming_deliveries = iq.execute().count or 0

    return DashboardSummary(
        pending_sales_orders=pending_sales,
        delayed_sales_orders=delayed_sales,
        incoming_purchase_orders=incoming_deliveries,
        delayed_shipments=0,
        low_stock_products=0,
    )