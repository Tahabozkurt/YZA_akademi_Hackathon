from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import get_session
from app.models import Product

router = APIRouter(prefix="/products", tags=["products"])

###Listele
@router.get("/", response_model=list[Product])
def list_products(session: Session = Depends(get_session)):
    return session.exec(select(Product)).all()

##Ekle
@router.post("/", response_model=Product, status_code=201)
def create_product(product: Product, session: Session = Depends(get_session)):
    session.add(product)
    session.commit()
    session.refresh(product)
    return product

###Güncelle
@router.patch("/{product_id}/stock", response_model=Product)
def update_stock(product_id: int, stock_quantity: int, session: Session = Depends(get_session)):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product.stock_quantity = stock_quantity
    session.add(product)
    session.commit()
    session.refresh(product)
    return product
