from fastapi import APIRouter, Depends, HTTPException
from app.database import supabase
from app.models import Product

router = APIRouter(prefix="/products", tags=["products"])

###Listele
@router.get("/", response_model=list[Product])
def list_products():
    response = supabase.table("products").select("*").execute()
    return response.data

##Ekle
@router.post("/", response_model=Product, status_code=201)
def create_product(product: Product):
    # model_dump() kullandığımızda 'unit', 'stock', 'last_delivery' gibi
    # tüm alanlar SQL'deki karşılıklarıyla Supabase'e gider.
    product_data = product.model_dump(exclude_unset=True)

    try:
        response = supabase.table("products").insert(product_data).execute()
        if not response.data:
            raise HTTPException(status_code=400, detail="Ürün eklenemedi")
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


###Güncelle
@router.patch("/{product_id}/stock", response_model=Product)
def update_stock(product_id: int, stock: int):
    try:
        response = supabase.table("products") \
            .update({"stock": stock}) \
            .eq("id", product_id) \
            .execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Ürün bulunamadı")
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))