from core.database import get_engine
import sqlalchemy as db

def create_table():
    engine = get_engine()
    with engine.connect() as conn:
        conn.execute(db.text("""
            CREATE TABLE IF NOT EXISTS sensor_data (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP NOT NULL,
                batch_id VARCHAR(50) NOT NULL,
                temps FLOAT NOT NULL,
                pH FLOAT,
                temperature FLOAT,
                dissolved_oxygen FLOAT
            );
        """))
        conn.commit()
    print("Table 'sensor_data' vérifiée/créée avec succès dans PostgreSQL !")

if __name__ == "__main__":
    create_table()