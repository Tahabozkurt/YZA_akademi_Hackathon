# YOLLAR YENİ KLASÖR YAPISINA GÖRE GÜNCELLENDİ
from backend.database import supabase
from backend.ai_agent import analyze_customer_message, draft_restock_email

def generate_bot_response(user_message: str, user_id: str = None) -> dict:
    ai_data = analyze_customer_message(user_message)
    intent = ai_data.get("intent")
    entity = ai_data.get("entity")
    
    bot_reply = "Size nasıl yardımcı olabilirim?"
    email_draft = None

    if intent == "siparis_durumu" and entity:
        query = supabase.table("orders").select("status, tracking_link, estimated_delivery, products(name)").eq("order_number", entity)
        # Web'den geliyorsa sadece o kişinin verisinde ara
        if user_id:
            query = query.eq("user_id", user_id)
            
        db_response = query.execute()
        
        if len(db_response.data) > 0:
            siparis = db_response.data[0]
            durum = siparis["status"]
            takip_linki = siparis.get("tracking_link")
            tahmini_tarih = siparis.get("estimated_delivery")
            urun_adi = siparis["products"]["name"] if siparis.get("products") else "Ürününüz"
            
            bot_reply = f"Kontrol ettim. {entity} numaralı ({urun_adi}) siparişinizin güncel durumu: {durum}."
            
            if tahmini_tarih:
                bot_reply += f" Paketinizin tahmini teslimat tarihi: {tahmini_tarih}."
            
            if takip_linki:
                bot_reply += f" Kargonuzu şu bağlantıdan takip edebilirsiniz: {takip_linki}"
        else:
            bot_reply = f"Sistemimizde {entity} numaralı bir sipariş bulamadım. Lütfen sipariş numaranızı kontrol edip tekrar deneyin."

    # --- GENEL STOK ÖZETİ ---
    elif intent == "genel_stok_ozeti":
        query = supabase.table("products").select("name, stock")
        if user_id:
            query = query.eq("user_id", user_id)
            
        db_response = query.execute()
        
        if len(db_response.data) > 0:
            bot_reply = "📦 **Genel Stok Özetiniz:**\n"
            kritik_urunler = []
            
            for urun in db_response.data:
                bot_reply += f"- {urun['name']}: {urun['stock']} adet\n"
                if urun['stock'] <= 10:
                    kritik_urunler.append(urun['name'])
            
            if kritik_urunler:
                bot_reply += f"\n⚠️ **Dikkat:** Şunların stoğu kritik seviyede: {', '.join(kritik_urunler)}"
        else:
            bot_reply = "Şu anda dükkanınızda kayıtlı hiçbir ürün bulunmuyor."

    # --- BEKLEYEN SİPARİŞLER ---
    elif intent == "bekleyen_siparisler":
        query = supabase.table("orders").select("order_number, quantity, products(name)").eq("status", "Hazırlanıyor")
        if user_id:
            query = query.eq("user_id", user_id)
            
        db_response = query.execute()
        
        if len(db_response.data) > 0:
            bot_reply = "🚀 **Operasyon Özeti - Hazırlanması Gereken Siparişler:**\n\n"
            
            for siparis in db_response.data:
                urun_adi = siparis["products"]["name"] if siparis.get("products") else "Silinmiş/Bilinmeyen Ürün"
                bot_reply += f"🔸 **{siparis['order_number']}** nolu sipariş: {siparis['quantity']} adet {urun_adi}\n"
                
            bot_reply += "\nKolay gelsin! Başka bir isteğiniz var mı?"
        else:
            bot_reply = "Harika haber! Şu an bekleyen veya hazırlanması gereken hiçbir siparişiniz yok, her şey yolunda."

    # --- TEKİL STOK SORGULAMA ---
    elif intent == "stok_sorgulama" and entity:
        query = supabase.table("products").select("name, stock").ilike("name", f"%{entity}%")
        if user_id:
            query = query.eq("user_id", user_id)
            
        db_response = query.execute()
        
        if len(db_response.data) > 0:
            urun = db_response.data[0]
            bot_reply = f"Evet, stoklarımızda {urun['stock']} adet {urun['name']} bulunmaktadır."
            
            kritik_esik = 10 
            if urun['stock'] <= kritik_esik:
                bot_reply += f" ⚠️ Dikkat: Stok seviyesi kritik eşiğin ({kritik_esik}) altında!"
                email_draft = draft_restock_email(urun['name'], urun['stock'])
        else:
            bot_reply = f"Maalesef şu an stoklarımızda '{entity}' isimli bir ürün bulunmamaktadır."

    return {
        "status": "success",
        "bot_reply": bot_reply,
        "ai_detected_intent": intent,
        "email_draft": email_draft
    }