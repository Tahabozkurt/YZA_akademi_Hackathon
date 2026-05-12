##Siparişler

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select


from app.database import get_session
from app.models import OrderStatus, SalesOrder
from app.schemas import StatusUpdate

router = APIRouter(prefix="/orders", tags=["sales orders"])


@router.get("/", response_model=list[SalesOrder])
def list_sales_orders(session: Session = Depends(get_session)):
    return session.exec(select(SalesOrder)).all()


@router.post("/", response_model=SalesOrder, status_code=201)
def create_sales_order(order: SalesOrder, session: Session = Depends(get_session)):
    session.add(order)
    session.commit()
    session.refresh(order)
    return order


@router.patch("/{order_id}/status", response_model=SalesOrder)
def update_sales_order_status(order_id: int, payload: StatusUpdate, session: Session = Depends(get_session)):
    order = session.get(SalesOrder, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Sales order not found")
    try:
        order.status = OrderStatus(payload.status)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid sales order status") from exc
    session.add(order)
    session.commit()
    session.refresh(order)
    return order
