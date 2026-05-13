from fastapi import APIRouter, HTTPException, Query
from backend.database import supabase
from backend.models import Delivery
from backend.schemas import StatusUpdate

router = APIRouter(prefix="/deliveries", tags=["deliveries"])

@router.get("/", response_model=list[dict])
def list_deliveries(user_id: str = Query(default=None)):
    q = supabase.table("deliveries").select("*, products(name, unit)")
    if user_id: q = q.eq("user_id", user_id)
    return q.execute().data

@router.post("/", response_model=dict, status_code=201)
def create_delivery(delivery: Delivery, user_id: str = Query(default=None)):
    data = delivery.model_dump(exclude_unset=True, mode='json')
    
    # KRİTİK ÇÖZÜM: Tedarik sayfasındaki boş verileri de temizle
    for field in ["date", "supplier", "notes"]:
        if data.get(field) == "":
            data[field] = None
            
    if user_id: data["user_id"] = user_id
    try:
        response = supabase.table("deliveries").insert(data).execute()
        new_delivery = response.data[0]
        
        if data.get("status") == "Tamamlandı":
            product_id = data["product_id"]
            prod_res = supabase.table("products").select("stock").eq("id", product_id).execute()
            if prod_res.data:
                current_stock = prod_res.data[0]["stock"]
                new_stock = current_stock + data["quantity"]
                supabase.table("products").update({"stock": new_stock, "last_delivery": data.get("date")}).eq("id", product_id).execute()

        return new_delivery
    except Exception as e:
        print(f"TEDARİK VERİTABANI HATASI: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/purchase-orders")
def get_purchase_orders(user_id: str = Query(default=None)):
    q = supabase.table("deliveries").select("*, products(name)").eq("type", "Stok Eklendi")
    if user_id: q = q.eq("user_id", user_id)
    return q.execute().data

# DUYGU'NUN MANTIĞI: Tedarik Tamamlanınca Stok Artar
@router.put("/{delivery_id}/complete")
def complete_delivery(delivery_id: int, user_id: str = Query(default=None)):
    q = supabase.table("deliveries").select("*").eq("id", delivery_id)
    if user_id: q = q.eq("user_id", user_id)
    delivery_res = q.execute()
    
    if not delivery_res.data: raise HTTPException(status_code=404, detail="Bulunamadı")
    delivery_data = delivery_res.data[0]
    
    if delivery_data["status"] == "Tamamlandı":
        return {"message": "Zaten tamamlanmış."}
        
    # Durumu güncelle
    supabase.table("deliveries").update({"status": "Tamamlandı"}).eq("id", delivery_id).execute()
    
    # Stoğu artır
    product_id = delivery_data["product_id"]
    prod_res = supabase.table("products").select("stock").eq("id", product_id).execute()
    if prod_res.data:
        current_stock = prod_res.data[0]["stock"]
        new_stock = current_stock + delivery_data["quantity"]
        supabase.table("products").update({"stock": new_stock, "last_delivery": delivery_data["date"]}).eq("id", product_id).execute()
        
    return {"message": "Teslim alındı ve stok güncellendi."}

# DUYGU'NUN MANTIĞI: Tedarik İptal Edilirse Stok Geri Çekilir
@router.put("/{delivery_id}/cancel")
def cancel_delivery(delivery_id: int, user_id: str = Query(default=None)):
    q = supabase.table("deliveries").select("*").eq("id", delivery_id)
    if user_id: q = q.eq("user_id", user_id)
    delivery_res = q.execute()
    
    if not delivery_res.data: raise HTTPException(status_code=404)
    delivery_data = delivery_res.data[0]
    
    if delivery_data["status"] == "İptal Edildi":
        return {"message": "Zaten iptal edilmiş."}
        
    # Eğer önceden "Tamamlandı" ise, eklenen stoğu geri çıkar
    if delivery_data["status"] == "Tamamlandı":
        product_id = delivery_data["product_id"]
        prod_res = supabase.table("products").select("stock").eq("id", product_id).execute()
        if prod_res.data:
            current_stock = prod_res.data[0]["stock"]
            new_stock = current_stock - delivery_data["quantity"]
            supabase.table("products").update({"stock": new_stock}).eq("id", product_id).execute()
            
    # İptal et
    supabase.table("deliveries").update({"status": "İptal Edildi"}).eq("id", delivery_id).execute()
    return {"message": "Teslimat iptal edildi."}

# DUYGU'NUN MANTIĞI: Tedarik Silinirse Stok Geri Çekilir
@router.delete("/{delivery_id}")
def delete_delivery(delivery_id: int, user_id: str = Query(default=None)):
    q = supabase.table("deliveries").select("*").eq("id", delivery_id)
    if user_id: q = q.eq("user_id", user_id)
    delivery_res = q.execute()
    
    if delivery_res.data:
        delivery_data = delivery_res.data[0]
        # Eğer "Tamamlandı" olan bir tedarik siliniyorsa stoğu geri düş
        if delivery_data["status"] == "Tamamlandı":
            product_id = delivery_data["product_id"]
            prod_res = supabase.table("products").select("stock").eq("id", product_id).execute()
            if prod_res.data:
                current_stock = prod_res.data[0]["stock"]
                new_stock = current_stock - delivery_data["quantity"]
                supabase.table("products").update({"stock": new_stock}).eq("id", product_id).execute()

    q_del = supabase.table("deliveries").delete().eq("id", delivery_id)
    if user_id: q_del = q_del.eq("user_id", user_id)
    q_del.execute()
    return {"status": "deleted", "message": "Teslimat silindi ve stok düzenlendi"}