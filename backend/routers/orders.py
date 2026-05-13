import uuid
from fastapi import APIRouter, HTTPException, Query
from backend.database import supabase
from backend.models import SalesOrder

router = APIRouter(prefix="/orders", tags=["sales orders"])

@router.get("/", response_model=list[dict])
def list_sales_orders(user_id: str = Query(default=None)):
    q = supabase.table("orders").select("*, products(name)")
    if user_id: q = q.eq("user_id", user_id)
    data = q.execute().data
    for item in data:
        item["product_name"] = item["products"]["name"] if item.get("products") and item["products"].get("name") else "Bilinmeyen Ürün"
    return data

@router.post("/", response_model=dict, status_code=201)
def create_sales_order(order: SalesOrder, user_id: str = Query(default=None)):
    order_data = order.model_dump(exclude_unset=True, mode='json')
    
    # KRİTİK ÇÖZÜM: Boş stringleri (özellikle tarih) None'a çeviriyoruz. 
    # Supabase boş string("") görünce tarih formatı sanıp çökmeyecek!
    for field in ["estimated_delivery", "tracking_link", "notes", "order_number"]:
        if order_data.get(field) == "":
            order_data[field] = None

    if user_id: order_data["user_id"] = user_id
    
    # Sipariş numarası boşsa (None olduysa), otomatik üret
    if not order_data.get("order_number"):
        order_data["order_number"] = f"SP-{uuid.uuid4().hex[:6].upper()}"
        
    try:
        prod_id = order_data.get("product_id")
        qty = order_data.get("quantity", 1)
        
        product_res = supabase.table("products").select("stock").eq("id", prod_id).execute()
        
        if product_res.data:
            current_stock = product_res.data[0].get("stock", 0)
            if current_stock >= qty:
                new_stock = current_stock - qty
                supabase.table("products").update({"stock": new_stock}).eq("id", prod_id).execute()
            else:
                raise HTTPException(status_code=400, detail=f"Yetersiz stok! Mevcut: {current_stock}")
        else:
            raise HTTPException(status_code=404, detail="Sipariş edilen ürün bulunamadı.")

        response = supabase.table("orders").insert(order_data).execute()
        return response.data[0]

    except HTTPException:
        raise
    except Exception as e:
        # Eğer yine de bir hata olursa terminale asıl sebebi bassın
        print(f"VERİTABANI HATASI (Sipariş): {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{order_id}")
def update_full_order(order_id: int, payload: dict, user_id: str = Query(default=None)):
    # Güncelleme işleminde de aynı boş string temizliğini yapıyoruz
    for field in ["estimated_delivery", "tracking_link", "notes", "order_number"]:
        if payload.get(field) == "":
            payload[field] = None

    q = supabase.table("orders").update(payload).eq("id", order_id)
    if user_id: q = q.eq("user_id", user_id)
    response = q.execute()
    return response.data[0]

@router.delete("/{order_id}")
def delete_order(order_id: int, user_id: str = Query(default=None)):
    q_order = supabase.table("orders").select("*").eq("id", order_id)
    if user_id: q_order = q_order.eq("user_id", user_id)
    order_res = q_order.execute()
    
    if order_res.data:
        order_data = order_res.data[0]
        product_id = order_data["product_id"]
        quantity = order_data["quantity"]
        
        prod_res = supabase.table("products").select("stock").eq("id", product_id).execute()
        if prod_res.data:
            current_stock = prod_res.data[0]["stock"]
            new_stock = current_stock + quantity
            supabase.table("products").update({"stock": new_stock}).eq("id", product_id).execute()

    q_del = supabase.table("orders").delete().eq("id", order_id)
    if user_id: q_del = q_del.eq("user_id", user_id)
    q_del.execute()
    return {"status": "deleted", "message": "Sipariş silindi ve stok geri yüklendi"}

@router.get("/shipments", response_model=list[dict])
def list_shipment_orders(user_id: str = Query(default=None)):
    q = supabase.table("orders").select("*, products(name)").in_("status", ["Kargoya Verildi", "Teslim Edildi", "Gecikmiş"])
    if user_id: q = q.eq("user_id", user_id)
    data = q.execute().data
    for item in data:
        item["product_name"] = item["products"]["name"] if item.get("products") and item["products"].get("name") else "Bilinmeyen Ürün"
    return data

@router.get("/track/{order_number}", response_model=dict)
def track_order(order_number: str):
    response = supabase.table("orders").select("*, products(name)").eq("order_number", order_number).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Sipariş bulunamadı")
    data = response.data[0]
    data["product_name"] = data["products"]["name"] if data.get("products") and data["products"].get("name") else "Bilinmeyen Ürün"
    return data