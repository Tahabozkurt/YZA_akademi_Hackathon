##Siparişler
from fastapi import APIRouter, Depends, HTTPException
##from app.models import OrderStatus, SalesOrder
#from app.schemas import StatusUpdate

###Yeniler
from app.database import supabase
from app.models import SalesOrder
from app.schemas import StatusUpdate

router = APIRouter(prefix="/orders", tags=["sales orders"])
## Siparişleri listele
@router.get("/", response_model=list[SalesOrder])
def list_sales_orders():
    response = supabase.table("orders").select("*").execute()
    return response.data

## Yeni sipariş oluşturma
@router.post("/", response_model=SalesOrder, status_code=201)
def create_sales_order(order: SalesOrder):
    order_data = order.model_dump(exclude_unset=True, mode='json')
    try:
        response = supabase.table("orders").insert(order_data).execute()
        if not response.data:
            raise HTTPException(status_code=400, detail="Sipariş oluşturulamadı")
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
## Sipariş durumu güncelleme
@router.patch("/{order_id}/status", response_model=SalesOrder)
def update_sales_order_status(order_id: int, payload: StatusUpdate):
    try:
        response = supabase.table("orders") \
            .update({"status": payload.status}) \
            .eq("id", order_id) \
            .execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Satış siparişi bulunamadı")
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Güncelleme hatası: {str(e)}")

@router.get("/test")
def test():
    response = supabase.table("orders").select("*").execute()
    return response.data