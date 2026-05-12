from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client, Client
import os
from typing import Optional, List

app = FastAPI()

# Frontend'in Backend'e erişebilmesi için CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supabase Bağlantı Ayarları
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://lanmrttuhqmneqsfockz.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imxhbm1ydHR1aHFtbmVxc2ZvY2t6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzg0MTI3NjYsImV4cCI6MjA5Mzk4ODc2Nn0.qkGwvBqvFhnLFSLi6cZtibMwuljf2yBBwMDTZ2PF1AQ")

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print(f"Supabase bağlantı hatası: {e}")
    supabase = None

# Pydantic modelleri
class ProductCreate(BaseModel):
    name: str
    unit: str
    stock: int
    last_delivery: Optional[str] = "-"

class ProductUpdate(BaseModel):
    name: str
    unit: str
    stock: int

class DeliveryCreate(BaseModel):
    product_id: int
    type: str
    quantity: int
    date: str
    supplier: Optional[str] = None
    notes: Optional[str] = None
    status: str
    update_stock: Optional[bool] = True

class OrderCreate(BaseModel):
    order_number: str
    customer_name: str
    product_id: int 
    quantity: int   
    status: str
    estimated_delivery: Optional[str] = None
    tracking_link: Optional[str] = None
    notes: Optional[str] = None

class OrderUpdate(BaseModel):
    status: str
    estimated_delivery: Optional[str] = None
    tracking_link: Optional[str] = None
    notes: Optional[str] = None

class StoreSettingsModel(BaseModel):
    name: str
    store_type: str
    units: List[str]
    contact_email: str
    contact_phone: Optional[str] = None
    rep_name: str

@app.get("/")
def read_root():
    return {"message": "Stok Yönetim API'sine Hoş Geldiniz. AI Bot Bağlantısı Hazır."}

# --- MAĞAZA AYARLARI (STORE SETTINGS) ENDPOINTLERİ ---

@app.get("/api/settings")
async def get_store_settings():
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase bağlantısı kurulamadı.")
    try:
        response = supabase.table("store_settings").select("*").eq("id", 1).execute()
        if not response.data:
            return None
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/settings")
async def update_store_settings(settings: StoreSettingsModel):
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase bağlantısı kurulamadı.")
    try:
        data = settings.model_dump()
        data["id"] = 1 # Hackathon prototipi için tek bir mağaza (ID=1) olduğunu varsayıyoruz
        
        # Önce kayıt var mı kontrol et
        existing = supabase.table("store_settings").select("*").eq("id", 1).execute()
        
        if existing.data:
            # Güncelle
            response = supabase.table("store_settings").update(data).eq("id", 1).execute()
        else:
            # Yeni Ekle
            response = supabase.table("store_settings").insert(data).execute()
            
        return response.data[0] if response.data else {"message": "Ayarlar kaydedildi"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# --- ÜRÜN (PRODUCT) ENDPOINTLERİ ---

@app.get("/api/products")
async def get_products():
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase bağlantısı kurulamadı.")
    try:
        response = supabase.table("products").select("*").order("id").execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/products/{product_id}")
async def get_product(product_id: int):
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase bağlantısı kurulamadı.")
    try:
        response = supabase.table("products").select("*").eq("id", product_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Ürün bulunamadı")
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/products")
async def create_product(product: ProductCreate):
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase bağlantısı kurulamadı.")
    try:
        data = product.model_dump() 
        response = supabase.table("products").insert(data).execute()
        return response.data[0] if response.data else {"message": "Eklendi"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/api/products/{product_id}")
async def update_product(product_id: int, product: ProductUpdate):
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase bağlantısı kurulamadı.")
    try:
        data = product.model_dump()
        response = supabase.table("products").update(data).eq("id", product_id).execute()
        return response.data[0] if response.data else {"message": "Güncellendi"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/api/products/{product_id}")
async def delete_product(product_id: int):
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase bağlantısı kurulamadı.")
    try:
        response = supabase.table("products").delete().eq("id", product_id).execute()
        return {"message": "Ürün silindi"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# --- TESLİMAT (DELIVERY) ENDPOINTLERİ ---

@app.get("/api/deliveries")
async def get_all_deliveries():
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase bağlantısı kurulamadı.")
    try:
        response = supabase.table("deliveries").select("*, products(name)").execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/products/{product_id}/deliveries")
async def get_deliveries_by_product(product_id: int):
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase bağlantısı kurulamadı.")
    try:
        response = supabase.table("deliveries").select("*").eq("product_id", product_id).order("date", desc=True).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/deliveries/{delivery_id}")
async def get_delivery(delivery_id: int):
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase bağlantısı kurulamadı.")
    try:
        response = supabase.table("deliveries").select("*, products(name, unit)").eq("id", delivery_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Teslimat bulunamadı")
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/deliveries")
async def create_delivery(delivery: DeliveryCreate):
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase bağlantısı kurulamadı.")
    try:
        data_to_db = delivery.model_dump(exclude={"update_stock"})
        
        if data_to_db.get('supplier') == '':
            data_to_db['supplier'] = None
        if data_to_db.get('notes') == '':
            data_to_db['notes'] = None
            
        response = supabase.table("deliveries").insert(data_to_db).execute()
        
        if delivery.status == "Tamamlandı" and delivery.update_stock:
            product_id = delivery.product_id
            prod_response = supabase.table("products").select("stock").eq("id", product_id).execute()
            if prod_response.data:
                current_stock = prod_response.data[0]["stock"]
                new_stock = current_stock + delivery.quantity
                supabase.table("products").update({"stock": new_stock, "last_delivery": delivery.date}).eq("id", product_id).execute()

        return response.data[0] if response.data else {"message": "Teslimat eklendi"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/api/deliveries/{delivery_id}/complete")
async def complete_delivery(delivery_id: int):
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase bağlantısı kurulamadı.")
    try:
        delivery_response = supabase.table("deliveries").select("*").eq("id", delivery_id).execute()
        if not delivery_response.data:
            raise HTTPException(status_code=404, detail="Teslimat bulunamadı")
            
        delivery_data = delivery_response.data[0]
        
        if delivery_data["status"] == "Tamamlandı":
            return {"message": "Zaten tamamlanmış."}
            
        supabase.table("deliveries").update({"status": "Tamamlandı"}).eq("id", delivery_id).execute()
        
        product_id = delivery_data["product_id"]
        prod_response = supabase.table("products").select("stock").eq("id", product_id).execute()
        if prod_response.data:
            current_stock = prod_response.data[0]["stock"]
            new_stock = current_stock + delivery_data["quantity"]
            supabase.table("products").update({"stock": new_stock, "last_delivery": delivery_data["date"]}).eq("id", product_id).execute()
            
        return {"message": "Teslim alındı ve stok güncellendi."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/api/deliveries/{delivery_id}")
async def delete_delivery(delivery_id: int):
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase bağlantısı kurulamadı.")
    try:
        # 1. Silinmek istenen teslimatın detaylarını al
        delivery_response = supabase.table("deliveries").select("*").eq("id", delivery_id).execute()
        if not delivery_response.data:
             raise HTTPException(status_code=404, detail="Silinecek teslimat bulunamadı")
             
        delivery_data = delivery_response.data[0]
        
        # 2. Eğer teslimat önceden "Tamamlandı" olarak işaretlenmişse ve stoğa etki etmişse stoğu geri al
        if delivery_data["status"] == "Tamamlandı":
            product_id = delivery_data["product_id"]
            prod_response = supabase.table("products").select("stock").eq("id", product_id).execute()
            if prod_response.data:
                current_stock = prod_response.data[0]["stock"]
                # Teslimat eklenmişse çıkart, satış olarak çıkmışsa ekle (ters işlem)
                # quantity değişkenimiz satışlarda zaten eksi (-) değer taşıdığı için
                # current_stock - quantity yapmak işlemi tersine çevirir.
                reverted_stock = current_stock - delivery_data["quantity"]
                supabase.table("products").update({"stock": reverted_stock}).eq("id", product_id).execute()

        # 3. Son olarak kaydı tablodan sil
        response = supabase.table("deliveries").delete().eq("id", delivery_id).execute()
        return {"message": "Teslimat silindi ve stok düzenlendi"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# --- SİPARİŞ TAKİBİ (ORDERS) ENDPOINTLERİ ---

@app.get("/api/orders")
async def get_orders():
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase bağlantısı kurulamadı.")
    try:
        # Bot'un ürün adını görebilmesi için product tablosuyla join yapıyoruz
        response = supabase.table("orders").select("*, products(name)").order("created_at", desc=True).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/orders")
async def create_order(order: OrderCreate):
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase bağlantısı kurulamadı.")
    try:
        data = order.model_dump()
        
        if data.get('estimated_delivery') == '':
            data['estimated_delivery'] = None
        if data.get('tracking_link') == '':
            data['tracking_link'] = None
        if data.get('notes') == '':
            data['notes'] = None
            
        # 1. Önce siparişi veritabanına ekle
        response = supabase.table("orders").insert(data).execute()
        
        # 2. Ürünün stoğundan sipariş miktarını düş
        product_id = data["product_id"]
        prod_response = supabase.table("products").select("stock").eq("id", product_id).execute()
        if prod_response.data:
            current_stock = prod_response.data[0]["stock"]
            new_stock = current_stock - data["quantity"]
            
            # Stoğu eksiye düşürmemek için kontrol (Opsiyonel ama mantıklı)
            if new_stock < 0:
                 new_stock = 0 
                 
            supabase.table("products").update({"stock": new_stock}).eq("id", product_id).execute()
            
        return response.data[0] if response.data else {"message": "Sipariş eklendi ve stok düşüldü"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/api/orders/{order_id}")
async def update_order(order_id: int, order: OrderUpdate):
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase bağlantısı kurulamadı.")
    try:
        data = order.model_dump()
        
        if data.get('estimated_delivery') == '':
            data['estimated_delivery'] = None
        if data.get('tracking_link') == '':
            data['tracking_link'] = None
        if data.get('notes') == '':
            data['notes'] = None
            
        response = supabase.table("orders").update(data).eq("id", order_id).execute()
        return response.data[0] if response.data else {"message": "Sipariş güncellendi"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/api/orders/{order_id}")
async def delete_order(order_id: int):
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase bağlantısı kurulamadı.")
    try:
        # Bot'un doğru stok söylemesi için iptal edilen siparişin stoğunu geri ekliyoruz
        order_response = supabase.table("orders").select("*").eq("id", order_id).execute()
        if order_response.data:
             order_data = order_response.data[0]
             product_id = order_data["product_id"]
             prod_response = supabase.table("products").select("stock").eq("id", product_id).execute()
             
             if prod_response.data:
                 current_stock = prod_response.data[0]["stock"]
                 # Sipariş silindiği için stoğu müşteriye giden miktar kadar artırıyoruz
                 new_stock = current_stock + order_data["quantity"]
                 supabase.table("products").update({"stock": new_stock}).eq("id", product_id).execute()

        # Kaydı sil
        response = supabase.table("orders").delete().eq("id", order_id).execute()
        return {"message": "Sipariş silindi ve stok geri yüklendi"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/orders/track/{order_number}")
async def track_order(order_number: str):
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase bağlantısı kurulamadı.")
    try:
        # Bot'un ve müşterinin ürünü de görebilmesi için join yapıyoruz
        response = supabase.table("orders").select("*, products(name)").eq("order_number", order_number).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Sipariş bulunamadı")
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
