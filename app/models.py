from __future__ import annotations
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from sqlalchemy import Column, DateTime, String
from sqlmodel import Field, SQLModel

#Durumlar
class OrderStatus(str, Enum):
    pending = "pending"; preparing = "preparing"; shipped = "shipped"
    delivered = "delivered"; delayed = "delayed"; cancelled = "cancelled"

class PurchaseStatus(str, Enum):
    planned = "planned"; ordered = "ordered"; in_transit = "in_transit"
    arrived = "arrived"; delayed = "delayed"; cancelled = "cancelled"

class ShipmentStatus(str, Enum):
    label_created = "label_created"; in_transit = "in_transit"
    out_for_delivery = "out_for_delivery"; delivered = "delivered"
    delayed = "delayed"; failed = "failed"

class Supplier(SQLModel, table=True):
    __tablename__ = "supplier"  # Senin Supabase isminle aynı yaptım
    __table_args__ = {"schema": "public"}
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    email: Optional[str] = None
    phone: Optional[str] = None
    lead_time_days: int = Field(default=3, ge=0)

class Product(SQLModel, table=True):
    __tablename__ = "product"
    __table_args__ = {"schema": "public"}
    id: Optional[int] = Field(default=None, primary_key=True)
    sku: str = Field(sa_column=Column(String, unique=True, index=True, nullable=False))
    name: str = Field(index=True)
    stock_quantity: int = Field(default=0, ge=0)
    reorder_threshold: int = Field(default=10, ge=0)
    supplier_id: Optional[int] = Field(default=None, foreign_key="public.supplier.id")

class SalesOrder(SQLModel, table=True):
    __tablename__ = "salesorder"
    __table_args__ = {"schema": "public"}
    id: Optional[int] = Field(default=None, primary_key=True)
    customer_name: str
    customer_phone: Optional[str] = None
    product_id: int = Field(foreign_key="public.product.id")
    quantity: int = Field(default=1, gt=0)
    status: OrderStatus = Field(default=OrderStatus.pending, index=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )
    promised_delivery_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), index=True, nullable=False)
    )
    notes: Optional[str] = None

class PurchaseOrder(SQLModel, table=True):
    __tablename__ = "purchaseorder"
    __table_args__ = {"schema": "public"}

    id: Optional[int] = Field(default=None, primary_key=True)
    supplier_name: str = Field(index=True)
    supplier_email: Optional[str] = None
    supplier_phone: Optional[str] = None

    product_id: int = Field(foreign_key="public.product.id")
    quantity: int = Field(gt=0)
    status: PurchaseStatus = Field(default=PurchaseStatus.planned, index=True)

    ordered_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    expected_arrival_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), index=True, nullable=False)
    )
    notes: Optional[str] = None

class Shipment(SQLModel, table=True):
    __tablename__ = "shipment"
    __table_args__ = {"schema": "public"}

    id: Optional[int] = Field(default=None, primary_key=True)
    sales_order_id: int = Field(foreign_key="public.salesorder.id")
    status: ShipmentStatus = Field(default=ShipmentStatus.label_created, index=True)

    shipped_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True)
    )
    estimated_delivery_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), index=True, nullable=False)
    )
    delivered_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True)
    )
