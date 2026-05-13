from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from twilio.twiml.messaging_response import MessagingResponse
from fastapi import Request, Form, Response


# Bütün yollar klasörüne uygun şekilde backend.routers oldu
from backend.routers import products, orders, purchase_orders, dashboard, calendar, settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 HACKATHON AI Altyapısı - Supabase Bağlantısı Hazır.")
    yield
    print("🛑 Uygulama kapatılıyor.")

app = FastAPI(title="SaaS Stok ve Kargo Yönetimi", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotaların hepsi /api altında toplandı
app.include_router(calendar.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(products.router, prefix="/api")
app.include_router(orders.router, prefix="/api")
app.include_router(purchase_orders.router, prefix="/api")
app.include_router(settings.router, prefix="/api")

@app.get("/")
def health_check():
    return {"status": "online", "message": "API Sistemleri Başarıyla Çalışıyor."}

# --- YAPAY ZEKA (AI BOT) BAĞLANTISI ---
from pydantic import BaseModel
class ChatRequest(BaseModel):
    message: str
    user_id: str

@app.post("/api/bot/chat")
async def chat_with_ai(request: ChatRequest):
    # TERMINALE LOG BAS: Gelen mesajı görelim
    print(f"🤖 BOT İSTEĞİ - Mesaj: {request.message} | UserID: {request.user_id}")
    
    try:
        from backend.bot_service import generate_bot_response
        
        # Bot_service'i çalıştırıyoruz
        res = generate_bot_response(request.message, request.user_id)
        
        # TERMINALE LOG BAS: Botun hazırladığı cevabı görelim
        bot_metni = res.get("bot_reply")
        print(f"✅ BOT CEVABI: {bot_metni}")
        
        # CRITICAL: Frontend 'reply' anahtarını beklediği için dönüşü böyle yapıyoruz
        return {"reply": bot_metni}
        
    except Exception as e:
        print(f"❌ BOT HATASI: {str(e)}")
        return {"reply": f"Hata: {str(e)}"}
    
    
# --- TWILIO WHATSAPP WEBHOOK (Hata Veren Kısım Düzeltildi) ---
@app.post("/webhook/twilio") # Logdaki hataya uygun adres burası
async def whatsapp_bot(request: Request):
    try:
        form_data = await request.form()
        user_msg = form_data.get("Body")
        
        # Senin terminal loglarında gördüğümüz o meşhur UID
        test_user_id = "b270705a-a674-4492-a6b0-8abf4bd15ff6" 
        
        from backend.bot_service import generate_bot_response
        res = generate_bot_response(user_msg, test_user_id)
        bot_reply = res.get("bot_reply", "Şu an cevap veremiyorum.")
        
        from twilio.twiml.messaging_response import MessagingResponse
        twiml = MessagingResponse()
        twiml.message(bot_reply)
        
        # Response importunun en üstte olduğundan emin ol!
        return Response(content=str(twiml), media_type="application/xml")
        
    except Exception as e:
        print(f"❌ WhatsApp Hatası: {e}")
        return Response(content="<Response><Message>Hata oluştu.</Message></Response>", media_type="application/xml")