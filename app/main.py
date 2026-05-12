##Kontrol edilicek
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import create_db_and_tables
from app.routers import calendar, orders, products, dashboard, shipments, purchase_orders, suppliers
from app.seed import seed_data

##Kontrol edilicek
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    #seed_data()
    yield


app = FastAPI(title="Takvim",lifespan=lifespan,)

##canlıya alınca değiştir
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


##End  Pointler
app.include_router(calendar.router)
app.include_router(dashboard.router)
app.include_router(products.router)
app.include_router(suppliers.router)
app.include_router(orders.router)
app.include_router(purchase_orders.router)
app.include_router(shipments.router)

##Kontrol çalışıyor mu vs
@app.get("/")
def health_check():
    return {
        "durum": "çalışıyor",
        "dokümantasyon": "/docs",
        "takvim_etkinlikleri": "/calendar/events"}
