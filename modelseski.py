#from __future__ import annotations

#from datetime import datetime
from enum import Enum
#from typing import Optional

#from sqlmodel import Field, SQLModel

##Durumlar -----------------------
#class OrderStatus(str, Enum):
#    pending = "pending"
#    preparing = "preparing"
#    shipped = "shipped"
#    delivered = "delivered"
#    delayed = "delayed"
#    cancelled = "cancelled"


#class PurchaseStatus(str, Enum):
#    planned = "planned"
#    ordered = "ordered"
#    in_transit = "in_transit"
#    arrived = "arrived"
#    delayed = "delayed"
#    cancelled = "cancelled"


#class ShipmentStatus(str, Enum):
 #   label_created = "label_created"
 #   in_transit = "in_transit"
 #   out_for_delivery = "out_for_delivery"
 #   delivered = "delivered"
 #   delayed = "delayed"
 #   failed = "failed"


#class Supplier(SQLModel, table=True):
#    id: Optional[int] = Field(default=None, primary_key=True)
#    name: str = Field(index=True)
#    email: Optional[str] = None
#    phone: Optional[str] = None
#    lead_time_days: int = Field(default=3, ge=0)

###Ürün geçici olarak var bu daha sonra ortak tabloya bağlanıcak
#class Product(SQLModel, table=True):
#    id: Optional[int] = Field(default=None, primary_key=True)
#    sku: str = Field(index=True, unique=True)
#    name: str = Field(index=True)
#    stock_quantity: int = Field(default=0, ge=0)
#    reorder_threshold: int = Field(default=10, ge=0)
#    supplier_id: Optional[int] = Field(default=None, foreign_key="supplier.id")

###Siparişlerle ilgili işlemler
#class SalesOrder(SQLModel, table=True):
#    id: Optional[int] = Field(default=None, primary_key=True)
#    customer_name: str
#    customer_phone: Optional[str] = None
#    product_id: int = Field(foreign_key="product.id")
#    quantity: int = Field(default=1, gt=0)
#    status: OrderStatus = Field(default=OrderStatus.pending, index=True)
#    created_at: datetime = Field(default_factory=datetime.utcnow)
#    promised_delivery_at: datetime = Field(index=True)
#    notes: Optional[str] = None


#class PurchaseOrder(SQLModel, table=True):
#    id: Optional[int] = Field(default=None, primary_key=True)
#    supplier_name: str = Field(index=True)
    #supplier_email: Optional[str] = None
    #supplier_phone: Optional[str] = None
   # product_id: int = Field(foreign_key="product.id")
  #  quantity: int = Field(gt=0)
#    status: PurchaseStatus = Field(default=PurchaseStatus.planned, index=True)
#    ordered_at: datetime = Field(default_factory=datetime.utcnow)
#    expected_arrival_at: datetime = Field(index=True)
 #   notes: Optional[str] = None


class Shipment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    sales_order_id: int = Field(foreign_key="salesorder.id")

    status: ShipmentStatus = Field(default=ShipmentStatus.label_created, index=True)
    shipped_at: Optional[datetime] = None
    estimated_delivery_at: datetime = Field(index=True)
    delivered_at: Optional[datetime] = None
