###Tedarikçi listesi

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.database import get_session
from app.models import Supplier

router = APIRouter(prefix="/suppliers", tags=["suppliers"])

###Tedarikçi listesini çek
@router.get("/", response_model=list[Supplier])
def list_suppliers(session: Session = Depends(get_session)):
    return session.exec(select(Supplier)).all()

####Tedarikçi ekle
@router.post("/", response_model=Supplier, status_code=201)
def create_supplier(supplier: Supplier, session: Session = Depends(get_session)):
    session.add(supplier)
    session.commit()
    session.refresh(supplier)
    return supplier
