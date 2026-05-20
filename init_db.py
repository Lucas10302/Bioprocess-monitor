from core.database import get_engine
import sqlalchemy as db

def init_tables():
    engine = get_engine()
    with engine.connect() as conn:
        print("🔧 Destruction forcée de l'ancienne table...")
        conn.execute(db.text("DROP TABLE IF EXISTS sensor_data CASCADE;"))
        
        print("🔨 Création de la table avec Agitation et Aération...")
        conn.execute(db.text("""
            CREATE TABLE sensor_data (
                id SERIAL,
                timestamp TIMESTAMP NOT NULL,
                batch_id VARCHAR(50) NOT NULL,
                temps FLOAT NOT NULL,
                pH FLOAT,
                temperature FLOAT,
                dissolved_oxygen FLOAT,
                agitation FLOAT,
                aeration FLOAT,
                PRIMARY KEY (timestamp, id)
            );
        """))
        
        try:
            conn.execute(db.text("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;"))
            conn.execute(db.text("SELECT create_hypertable('sensor_data', 'timestamp', if_not_exists => TRUE);"))
            print("🚀 Table 'sensor_data' convertie en Hypertable TimescaleDB !")
        except Exception as e:
            pass

        conn.execute(db.text("""
            CREATE TABLE IF NOT EXISTS audit_trail (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                utilisateur VARCHAR(50) NOT NULL,
                action VARCHAR(100) NOT NULL,
                details TEXT
            );
        """))
        
        conn.commit()
    print("✅ Base de données PARFAITEMENT initialisée !")

if __name__ == "__main__":
    init_tables()