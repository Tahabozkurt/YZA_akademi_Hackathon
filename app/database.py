import os
from sqlmodel import SQLModel, Session, create_engine
from dotenv import load_dotenv
##.envden gizli bilgileri çektik
load_dotenv()
##.envden database i çek
DATABASE_URL = os.getenv("DATABASE_URL")

###Çalıştığını kontrol ediyoruz
if not DATABASE_URL:
    raise ValueError("HATA: DATABASE_URL .env dosyasında bulunamadı! Formatı kontrol edin.")

engine = create_engine(DATABASE_URL, echo=True)

##Tablolar var ancak yine de sqlite tan bıraktım
def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
