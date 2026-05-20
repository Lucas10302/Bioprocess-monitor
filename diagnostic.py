import os
import sqlalchemy as db
from dotenv import load_dotenv

# On charge le .env pour être sûr de l'URL
load_dotenv()
DB_URL = os.getenv("DB_URL")

print(f"🔗 URL utilisée : {DB_URL}")

try:
    engine = db.create_engine(DB_URL)
    with engine.connect() as conn:
        # 1. On compte les lignes
        count = conn.execute(db.text("SELECT COUNT(*) FROM sensor_data;")).scalar()
        print(f"📊 Lignes réellement présentes dans la base : {count}")
        
        # 2. On regarde les noms des batches
        batches = conn.execute(db.text("SELECT DISTINCT batch_id FROM sensor_data;")).fetchall()
        print(f"🏷️ Batches trouvés : {[b[0] for b in batches]}")

except Exception as e:
    print(f"❌ Erreur critique : {e}")