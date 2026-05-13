from __future__ import annotations
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from sqlalchemy import Column, DateTime, String
from sqlmodel import Field, SQLModel

# Durumlar
class OrderStatus(str, Enum):
    pending = "beklemede"
    preparing = "hazırlanıyor"
    shipped = "sevk edildi"
    delivered = "teslim edildi"
    delayed = "gecikmiş"
    cancelled = "iptal edildi"

class PurchaseStatus(str, Enum):
    planned = "planlandı"
    ordered = "sipariş verildi"
    in_transit = "yolda/aktarmada"
    arrived = "ulaştı"
    delayed = "gecikmiş"
    cancelled = "iptal edildi"

class ShipmentStatus(str, Enum):
    label_created = "kargo etiketi oluşturuldu"
    in_transit = "yolda"
    out_for_delivery = "dağıtıma çıktı"
    delivered = "teslim edildi"
    delayed = "gecikmiş"
    failed = "teslimat başarısız"

class Product(SQLModel):
    __tablename__ = "products"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    unit: Optional[str] = None
    stock: int = Field(default=0, ge=0)
    last_delivery: Optional[str] = None
    user_id: Optional[str] = None

class SalesOrder(SQLModel):
    __tablename__ = "orders"
    id: Optional[int] = Field(default=None, primary_key=True)
    order_number: Optional[str] = None
    customer_name: str
    product_id: int
    quantity: int = Field(default=1, gt=0)
    status: str = Field(default="Beklemede")
    estimated_delivery: Optional[str] = None
    delivery_address: Optional[str] = None
    tracking_link: Optional[str] = None
    shipped_at: Optional[str] = None
    delivered_at: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[str] = None
    user_id: Optional[str] = None

class Delivery(SQLModel):
    __tablename__ = "deliveries"
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int
    type: str = Field(default="Stok Eklendi")
    quantity: int = Field(gt=0)
    date: str
    supplier: Optional[str] = None
    status: str = Field(default="Planlandı")
    notes: Optional[str] = None
    user_id: Optional[str] = None

class StoreSetting(SQLModel):
    __tablename__ = "store_settings"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    store_type: Optional[str] = None
    units: Optional[list[str]] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    rep_name: Optional[str] = None
    created_at: Optional[str] = None
    user_id: Optional[str] = None