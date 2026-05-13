from fastapi import APIRouter, HTTPException, Query
from backend.database import supabase
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/settings", tags=["settings"])

class StoreSettingsModel(BaseModel):
    name: str
    store_type: Optional[str] = None
    units: Optional[List[str]] = []
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    rep_name: Optional[str] = None

@router.get("/")
def get_settings(user_id: str = Query(default=None)):
    if not user_id:
        return {"name": "Mağaza Ayarlanmadı"}
    
    try:
        res = supabase.table("store_settings").select("*").eq("user_id", user_id).execute()
        if res.data:
            return res.data[0]
        
        return {"name": "Yeni Mağaza", "is_new": True}
        
    except Exception as e:
        print(f"Settings Fetch Error: {e}")
        return {"name": "Hata Oluştu"}

@router.post("/")
def save_settings(settings: StoreSettingsModel, user_id: str = Query(default=None)):
    if not user_id:
        raise HTTPException(status_code=401, detail="Kullanıcı kimliği eksik.")
        
    data = settings.model_dump(exclude_unset=True)
    data["user_id"] = user_id
    
    try:
        existing = supabase.table("store_settings").select("id").eq("user_id", user_id).execute()
        
        if existing.data:
            # Varsa güncelle
            res = supabase.table("store_settings").update(data).eq("user_id", user_id).execute()
        else:
            # YOKSA YENİ EKLE (Otomatik ID Hatası İçin Manuel ID Çözümü)
            # Supabase'deki en yüksek ID'yi bulup +1 ekliyoruz.
            max_id_res = supabase.table("store_settings").select("id").order("id", desc=True).limit(1).execute()
            
            next_id = 1
            if max_id_res.data:
                next_id = max_id_res.data[0]["id"] + 1
                
            data["id"] = next_id  # Veritabanına id'yi manuel olarak yolluyoruz
            
            res = supabase.table("store_settings").insert(data).execute()
            
        return res.data[0] if res.data else {"message": "Başarıyla kaydedildi"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Kaydetme Hatası: {str(e)}")