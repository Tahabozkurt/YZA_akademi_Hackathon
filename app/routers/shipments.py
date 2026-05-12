#Kargolar ve onunla ilgili işlemler

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import get_session
from app.models import Shipment, ShipmentStatus
from app.schemas import StatusUpdate

router = APIRouter(prefix="/shipments", tags=["shipments"])

###Kargoların listesini çek
@router.get("/", response_model=list[Shipment])
def list_shipments(session: Session = Depends(get_session)):
    return session.exec(select(Shipment)).all()

###Kargo işlemi ekle
@router.post("/", response_model=Shipment, status_code=201)
def create_shipment(shipment: Shipment, session: Session = Depends(get_session)):
    session.add(shipment)
    session.commit()
    session.refresh(shipment)
    return shipment

#Kargo işlemi güncelle
@router.patch("/{shipment_id}/status", response_model=Shipment)
def update_shipment_status(shipment_id: int, payload: StatusUpdate, session: Session = Depends(get_session)):
    shipment = session.get(Shipment, shipment_id)
    if not shipment:
        raise HTTPException(status_code=404, detail="Kargo/Gönderim bulunamadı")
    try:
        shipment.status = ShipmentStatus(payload.status)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Geçersiz gönderi/kargo durumu") from exc
    session.add(shipment)
    session.commit()
    session.refresh(shipment)
    return shipment
