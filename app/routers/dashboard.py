##Özetlerin Yer Aldığı Dashboard
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException
from app.database import supabase
from app.schemas import DashboardSummary

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/summary", response_model=DashboardSummary)
def dashboard_summary():
    now = datetime.utcnow()
    next_week = now + timedelta(days=14)

    # Bekleyen satışlar (orders tablosundan)
    pending_sales_res = supabase.table("orders") \
        .select("id", count="exact") \
        .in_("status", ["Beklemede", "Hazırlanıyor", "Kargoya Verildi"]) \
        .execute()
    pending_sales = pending_sales_res.count or 0

    # Gecikmiş satışlar
    delayed_sales_res = supabase.table("orders") \
        .select("id", count="exact") \
        .eq("status", "Gecikmiş") \
        .execute()
    delayed_sales = delayed_sales_res.count or 0

    # Yaklaşan teslimatlar (deliveries tablosundan, önümüzdeki 14 gün)
    incoming_deliveries_res = supabase.table("deliveries") \
        .select("id", count="exact") \
        .lte("date", next_week.strftime("%Y-%m-%d")) \
        .gte("date", now.strftime("%Y-%m-%d")) \
        .in_("status", ["Planlandı"]) \
        .execute()
    incoming_deliveries = incoming_deliveries_res.count or 0

    # Kritik stok uyarısı
    # reorder_threshold kolonu products tablosuna eklendikten sonra aktif edilecek
    # low_stock_res = supabase.table("products") \
    #     .select("id", count="exact") \
    #     .lt("stock", "reorder_threshold") \  # Supabase bu karşılaştırmayı desteklemiyor,
    #     .execute()                            # bunun için Supabase'de bir view veya RPC fonksiyonu yazılması gerekecek
    # low_stock = low_stock_res.count or 0
    low_stock = 0  # Şimdilik 0, yukarıdaki kısım teyit edilince aktif edilecek

    return DashboardSummary(
        pending_sales_orders=pending_sales,
        delayed_sales_orders=delayed_sales,
        incoming_purchase_orders=incoming_deliveries,
        delayed_shipments=0,  # Shipment tablosu eklenince aktif edilecek
        low_stock_products=low_stock,
    )