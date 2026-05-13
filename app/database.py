import os
#from sqlmodel import SQLModel, Session, create_engine
from supabase import create_client, Client
from dotenv import load_dotenv
##.envden gizli bilgileri çektik
load_dotenv()
##.envden database i çek
#DATABASE_URL = os.getenv("DATABASE_URL")
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")

###Çalıştığını kontrol ediyoruz
#if not DATABASE_URL:
#   raise ValueError("HATA: DATABASE_URL .env dosyasında bulunamadı! Formatı kontrol edin.")
if not url or not key:
    raise ValueError("HATA: .env dosyasında SUPABASE_URL veya SUPABASE_KEY eksik!")

supabase: Client = create_client(url, key)
def test_connection():
    try:
        # 'users' veya veritabanındaki herhangi bir tablonun adını yazabilirsin
        # Boş bir tablo olsa bile hata vermiyorsa bağlantı tamamdır.
        response = supabase.table("products").select("*", count="exact").limit(1).execute()
        print("Bağlantı başarılı! Veri çekildi.")
    except Exception as e:
        print(f"Bağlantı hatası: {e}")

if __name__ == "__main__":
    test_connection()


##engine = create_engine(DATABASE_URL, echo=True)

##Tablolar var ancak yine de sqlite tan bıraktım
#def create_db_and_tables() -> None:
#    SQLModel.metadata.create_all(engine)

#def get_session():
#    with Session(engine) as session:
#        yield session
