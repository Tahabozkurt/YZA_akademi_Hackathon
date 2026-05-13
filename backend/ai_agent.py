import os
import json # JSON işlemleri için ekledik
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.1
)

def analyze_customer_message(message: str):
    system_prompt = """
    Sen Hackathon projesi için çalışan zeki bir asistanın beynisin.
    Gelen müşteri mesajını analiz et ve SADECE aşağıdaki JSON formatında çıktı ver.
    Başka hiçbir açıklama metni yazma.

    Niyetler (intent) şunlar olabilir: 
    - "stok_sorgulama" (Örn: Zeytinyağı var mı?)
    - "genel_stok_ozeti" (Örn: Tüm stoklarımı özetle, depoda neler var?, stok durumum nedir?)
    - "bekleyen_siparisler" (Örn: Hazırlanması gereken siparişler neler?, Bugün kargoya verilecek neler var?)
    - "siparis_durumu" (Örn: 123 nolu siparişim nerede?)
    - "diger" (Örn: Merhaba, nasılsınız?)

    Çıktı Formatı:
    {{
        "intent": "bulunan_niyet",
        "entity": "varsa_ürün_adı_veya_sipariş_numarası_yoksa_null"
    }}
    """
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{user_message}")
    ])
    
    chain = prompt | llm
    response = chain.invoke({"user_message": message})
    
    # AI'dan gelen ham metin
    raw_content = response.content
    
    # Markdown etiketlerini temizle
    clean_content = raw_content.replace("```json", "").replace("```", "").strip()
    
    # Temizlenmiş metni Python Dictionary (Sözlük) yapısına çevir
    try:
        return json.loads(clean_content)
    except json.JSONDecodeError:
        return {"intent": "hata", "entity": None}
    
def draft_restock_email(product_name: str, stock_quantity: int):
    prompt_text = f"""
    Görev: Hackathon projesi olan akıllı asistan sistemisin.
    Durum: '{product_name}' ürününün stoğu kritik seviyeye ({stock_quantity} adet) düştü.
    Aksiyon: Tedarikçiye acil sipariş geçmek için net, okunması kolay ve profesyonel bir e-posta taslağı hazırla.
    
    Kurallar:
    1. Giriş cümlesini çok kısa tut.
    2. İstekleri (Miktar, Fiyat, Termin Süresi) maddeler (bullet points) halinde yaz.
    3. Konu başlığı (Subject) kesinlikle olsun.
    4. Kapanışta "hackathon Akıllı Asistanı" imzasını kullan.
    """
    
    response = llm.invoke(prompt_text)
    return response.content