###Tedarikle ilgili işlemler

from fastapi import APIRouter, HTTPException
from app.database import supabase
from app.models import Delivery
from app.schemas import StatusUpdate

router = APIRouter(prefix="/purchase-orders", tags=["purchase orders"])

# Teslimatları listele
@router.get("/", response_model=list[Delivery])
def list_deliveries():
    response = supabase.table("deliveries").select("*").execute()
    return response.data

# Yeni teslimat ekle
@router.post("/", response_model=Delivery, status_code=201)
def create_delivery(delivery: Delivery):
    data = delivery.model_dump(exclude_unset=True, mode='json')
    try:
        response = supabase.table("deliveries").insert(data).execute()
        if not response.data:
            raise HTTPException(status_code=400, detail="Teslimat oluşturulamadı")
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Teslimat durumu güncelle
@router.patch("/{delivery_id}/status", response_model=Delivery)
def update_delivery_status(delivery_id: int, payload: StatusUpdate):
    try:
        response = supabase.table("deliveries") \
            .update({"status": payload.status}) \
            .eq("id", delivery_id) \
            .execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Teslimat bulunamadı")
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Güncelleme hatası: {str(e)}")