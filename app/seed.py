from datetime import datetime, timedelta

from sqlmodel import Session, select

from app.database import engine

from app.models import (
    Product,
    PurchaseOrder,
    PurchaseStatus,
    SalesOrder,
    Shipment,
    ShipmentStatus,
    Supplier,
    OrderStatus,
)


def seed_data() -> None:
    with Session(engine) as session:
        existing = session.exec(select(Supplier)).first()
        if existing:
            return

        now = datetime.utcnow().replace(microsecond=0)

        supplier1 = Supplier(name="Ege Kooperatif Tedarik", email="tedarik@egekoop.test", lead_time_days=4)
        supplier2 = Supplier(name="Anadolu Paketleme", email="operasyon@anadolupaket.test", lead_time_days=2)
        session.add(supplier1)
        session.add(supplier2)
        session.commit()
        session.refresh(supplier1)
        session.refresh(supplier2)

        tomato = Product(sku="DOM-001", name="Domates 1kg", stock_quantity=32, reorder_threshold=50, supplier_id=supplier1.id)
        honey = Product(sku="BAL-250", name="Çiçek Balı 250g", stock_quantity=120, reorder_threshold=30, supplier_id=supplier1.id)
        box = Product(sku="KUTU-S", name="Küçük Kargo Kutusu", stock_quantity=8, reorder_threshold=20, supplier_id=supplier2.id)
        session.add(tomato)
        session.add(honey)
        session.add(box)
        session.commit()
        for product in [tomato, honey, box]:
            session.refresh(product)

        sales_orders = [
            SalesOrder(customer_name="Ayşe Yılmaz", product_id=tomato.id, quantity=12, status=OrderStatus.preparing, promised_delivery_at=now + timedelta(days=1, hours=4), notes="Sabah teslim istiyor"),
            SalesOrder(customer_name="Murat Demir", product_id=honey.id, quantity=3, status=OrderStatus.shipped, promised_delivery_at=now + timedelta(days=2), notes="Hediye paketi"),
            SalesOrder(customer_name="Zeynep Kaya", product_id=tomato.id, quantity=20, status=OrderStatus.delayed, promised_delivery_at=now - timedelta(days=1), notes="Stok eksikliği"),
        ]
        session.add_all(sales_orders)
        session.commit()
        for order in sales_orders:
            session.refresh(order)

        purchase_orders = [
            PurchaseOrder(supplier_id=supplier1.id, product_id=tomato.id, quantity=100, status=PurchaseStatus.in_transit, expected_arrival_at=now + timedelta(days=1, hours=2)),
            PurchaseOrder(supplier_id=supplier2.id, product_id=box.id, quantity=200, status=PurchaseStatus.ordered, expected_arrival_at=now + timedelta(days=3)),
            PurchaseOrder(supplier_id=supplier1.id, product_id=honey.id, quantity=50, status=PurchaseStatus.delayed, expected_arrival_at=now - timedelta(hours=10)),
        ]
        session.add_all(purchase_orders)
        session.commit()

        shipments = [
            Shipment(sales_order_id=sales_orders[1].id, carrier_name="Hızlı Kargo", tracking_code="HZ123456", status=ShipmentStatus.in_transit, shipped_at=now - timedelta(hours=12), estimated_delivery_at=now + timedelta(days=1)),
            Shipment(sales_order_id=sales_orders[2].id, carrier_name="Mavi Kargo", tracking_code="MV987654", status=ShipmentStatus.delayed, shipped_at=now - timedelta(days=3), estimated_delivery_at=now - timedelta(hours=6)),
        ]
        session.add_all(shipments)
        session.commit()
