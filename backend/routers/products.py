from fastapi import APIRouter, HTTPException, Query
from backend.database import supabase
from backend.models import Product

router = APIRouter(prefix="/products", tags=["products"])

@router.get("/", response_model=list[Product])
def list_products(user_id: str = Query(default=None)):
    q = supabase.table("products").select("*")
    if user_id: q = q.eq("user_id", user_id)
    return q.execute().data

@router.post("/", response_model=Product, status_code=201)
def create_product(product: Product, user_id: str = Query(default=None)):
    product_data = product.model_dump(exclude_unset=True)
    if user_id: product_data["user_id"] = user_id
    try:
        response = supabase.table("products").insert(product_data).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{product_id}")
def get_single_product(product_id: int, user_id: str = Query(default=None)):
    q = supabase.table("products").select("*").eq("id", product_id)
    if user_id: q = q.eq("user_id", user_id)
    res = q.execute()
    if not res.data: raise HTTPException(status_code=404, detail="Bulunamadı")
    return res.data[0]

@router.put("/{product_id}")
def update_full_product(product_id: int, payload: dict, user_id: str = Query(default=None)):
    q = supabase.table("products").update(payload).eq("id", product_id)
    if user_id: q = q.eq("user_id", user_id)
    res = q.execute()
    return res.data[0]

# ÇÖZÜM 2: SİLME İŞLEMİNE HATA YAKALAMA EKLENDİ
@router.delete("/{product_id}")
def delete_product(product_id: int, user_id: str = Query(default=None)):
    try:
        q = supabase.table("products").delete().eq("id", product_id)
        if user_id: q = q.eq("user_id", user_id)
        res = q.execute()
        
        if not res.data:
            raise HTTPException(status_code=404, detail="Silinecek ürün bulunamadı.")
            
        return {"status": "deleted"}
    except Exception as e:
        error_msg = str(e).lower()
        # Eğer yabancı anahtar (Foreign Key) hatası verirse bunu kullanıcıya düzgünce söyle
        if "foreign key constraint" in error_msg or "violates foreign key" in error_msg or "23503" in error_msg:
            raise HTTPException(
                status_code=400, 
                detail="Silme Başarısız: Bu ürüne ait geçmiş Sipariş veya Tedarik kayıtları bulunuyor. Önce ilgili sipariş/tedarik kayıtlarını silmelisiniz."
            )
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{product_id}/deliveries")
def get_product_deliveries(product_id: int, user_id: str = Query(default=None)):
    q = supabase.table("deliveries").select("*").eq("product_id", product_id)
    if user_id: q = q.eq("user_id", user_id)
    return q.execute().data