import os
import sqlalchemy as db
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# 🛡️ LE BOUCLIER ANTI-FANTÔME : override=True force l'utilisation du fichier .env 
# et écrase toutes les vieilles adresses bloquées dans la mémoire de Windows.
load_dotenv()

DB_URL = os.getenv("DB_URL")

# Mémorisation du moteur pour éviter de créer 1000 connexions en arrière-plan
_engine = None

def get_engine():
    """Retourne le moteur de connexion SQLAlchemy de manière optimisée."""
    global _engine
    if _engine is None:
        if not DB_URL:
            raise ValueError("L'URL de la base de données (DB_URL) est introuvable dans le .env")
        _engine = db.create_engine(DB_URL, isolation_level="AUTOCOMMIT")
    return _engine

def insert_row(batch_id, temps, pH, temperature, dissolved_oxygen, agitation=None, aeration=None, timestamp=None):
    """Insère une nouvelle mesure complète dans la base TimescaleDB."""
    if timestamp is None:
        timestamp = datetime.now()

    with get_engine().connect() as conn:
        conn.execute(db.text("""
            INSERT INTO sensor_data
                (timestamp, batch_id, temps, pH, temperature, dissolved_oxygen, agitation, aeration)
            VALUES
                (:timestamp, :batch_id, :temps, :pH, :temperature, :dissolved_oxygen, :agitation, :aeration)
        """), {
            "timestamp"        : timestamp,
            "batch_id"         : batch_id,
            "temps"            : temps,
            "pH"               : pH,
            "temperature"      : temperature,
            "dissolved_oxygen" : dissolved_oxygen,
            "agitation"        : agitation,
            "aeration"         : aeration
        })

def fetch_batch(batch_id, limit=None):
    """Récupère toutes les mesures d'un batch."""
    query  = """
        SELECT timestamp, batch_id, temps, pH, temperature, dissolved_oxygen, agitation, aeration
        FROM sensor_data
        WHERE batch_id = :batch_id
        ORDER BY timestamp ASC
    """
    if limit:
        query += f" LIMIT {limit}"

    with get_engine().connect() as conn:
        df = pd.read_sql(db.text(query), conn, params={"batch_id": batch_id})
    return df

def list_batches():
    """Retourne la liste de tous les batch_id disponibles."""
    with get_engine().connect() as conn:
        result = conn.execute(db.text("""
            SELECT DISTINCT batch_id,
                   MIN(timestamp) as start_time,
                   MAX(timestamp) as end_time,
                   COUNT(*) as n_points
            FROM sensor_data
            GROUP BY batch_id
            ORDER BY start_time DESC
        """))
        return pd.DataFrame(result.fetchall(), columns=["batch_id", "start_time", "end_time", "n_points"])

def delete_batch(batch_id):
    """Supprime toutes les données d'un batch."""
    with get_engine().connect() as conn:
        conn.execute(db.text("DELETE FROM sensor_data WHERE batch_id = :batch_id"), {"batch_id": batch_id})

def log_audit_action(utilisateur, action, details=""):
    """Enregistre une action dans le journal d'audit (Traçabilité)."""
    with get_engine().connect() as conn:
        conn.execute(db.text("""
            INSERT INTO audit_trail (utilisateur, action, details)
            VALUES (:u, :a, :d)
        """), {
            "u": utilisateur, 
            "a": action, 
            "d": details
        })

def log_audit_event(utilisateur, action, details):
    """Enregistre une action de manière indélébile dans l'Audit Trail."""
    with get_engine().connect() as conn:
        conn.execute(db.text("""
            CREATE TABLE IF NOT EXISTS audit_trail (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                utilisateur VARCHAR(50),
                action VARCHAR(100),
                details TEXT
            )
        """))
        conn.execute(db.text("""
            INSERT INTO audit_trail (utilisateur, action, details)
            VALUES (:utilisateur, :action, :details)
        """), {
            "utilisateur": utilisateur,
            "action": action,
            "details": details
        })