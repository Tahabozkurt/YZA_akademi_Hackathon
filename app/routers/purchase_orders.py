from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import get_session
from app.models import PurchaseOrder, PurchaseStatus
from app.schemas import StatusUpdate

router = APIRouter(prefix="/purchase-orders", tags=["purchase orders"])


@router.get("/", response_model=list[PurchaseOrder])
def list_purchase_orders(session: Session = Depends(get_session)):
    return session.exec(select(PurchaseOrder)).all()


@router.post("/", response_model=PurchaseOrder, status_code=201)
def create_purchase_order(order: PurchaseOrder, session: Session = Depends(get_session)):
    session.add(order)
    session.commit()
    session.refresh(order)
    return order


@router.patch("/{order_id}/status", response_model=PurchaseOrder)
def update_purchase_order_status(order_id: int, payload: StatusUpdate, session: Session = Depends(get_session)):
    order = session.get(PurchaseOrder, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    try:
        order.status = PurchaseStatus(payload.status)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid purchase order status") from exc
    session.add(order)
    session.commit()
    session.refresh(order)
    return order
