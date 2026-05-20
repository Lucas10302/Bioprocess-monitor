import asyncio
from asyncua import Client
import sys
import os

# Import de ta fonction d'insertion en base de données
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from core.database import insert_row

# ==========================================
# CONFIGURATION DU BIORÉACTEUR (OPC-UA)
# ==========================================
OPC_URL = "opc.tcp://localhost:4840/freeopcua/server/" 

NODE_PH   = "ns=2;s=pH_Sensor"
NODE_TEMP = "ns=2;s=Temp_Sensor"
NODE_DO   = "ns=2;s=DO_Sensor"
NODE_AGIT = "ns=2;s=Agitation_Sensor"
NODE_AER  = "ns=2;s=Aeration_Sensor" 

BATCH_ID = "Batch_Recherche_Live_002"
INTERVAL = 5  # Le capteur lit toujours toutes les 5s, mais n'écrit plus forcément

# --- NOUVEAU : PARAMÉTRAGE DU DEADBAND ---
# Si la variation est inférieure à ce chiffre, on n'enregistre pas dans la base
DEADBAND = {
    "pH": 0.05,               # Variation min de 0.05
    "temperature": 0.1,       # Variation min de 0.1 °C
    "dissolved_oxygen": 1.0,  # Variation min de 1.0 %
    "agitation": 3.0,         # Variation min de 3 RPM
    "aeration": 0.05          # Variation min de 0.05 L/min
}

async def main():
    print(f"Tentative de connexion au bioréacteur via {OPC_URL}...")
    client = Client(url=OPC_URL)
    
    try:
        await client.connect()
        print("✅ Connecté au bioréacteur avec succès !")

        var_ph   = client.get_node(NODE_PH)
        var_temp = client.get_node(NODE_TEMP)
        var_do   = client.get_node(NODE_DO)
        var_agit = client.get_node(NODE_AGIT)
        var_aer  = client.get_node(NODE_AER) 

        temps_ecoule_secondes = 0

        # --- NOUVEAU : MÉMOIRE DES DERNIÈRES VALEURS ENREGISTRÉES ---
        derniere_ecriture = {
            "pH": None, "temperature": None, "dissolved_oxygen": None, 
            "agitation": None, "aeration": None
        }

        while True:
            # 1. Lecture physique des sondes
            val_ph   = await var_ph.read_value()
            val_temp = await var_temp.read_value()
            val_do   = await var_do.read_value()
            val_agit = await var_agit.read_value()
            val_aer  = await var_aer.read_value() 

            temps_minutes = temps_ecoule_secondes / 60.0

            # 2. Logique décisionnelle du Deadband
            faut_il_sauvegarder = False

            # Si c'est la toute première mesure (la mémoire est vide), on force l'enregistrement
            if derniere_ecriture["pH"] is None:
                faut_il_sauvegarder = True
            else:
                # On vérifie chaque sonde. Si UNE SEULE dépasse son deadband, on déclenche l'enregistrement global
                if abs(val_ph - derniere_ecriture["pH"]) >= DEADBAND["pH"]: faut_il_sauvegarder = True
                if abs(val_temp - derniere_ecriture["temperature"]) >= DEADBAND["temperature"]: faut_il_sauvegarder = True
                if abs(val_do - derniere_ecriture["dissolved_oxygen"]) >= DEADBAND["dissolved_oxygen"]: faut_il_sauvegarder = True
                if abs(val_agit - derniere_ecriture["agitation"]) >= DEADBAND["agitation"]: faut_il_sauvegarder = True
                if abs(val_aer - derniere_ecriture["aeration"]) >= DEADBAND["aeration"]: faut_il_sauvegarder = True

            # 3. Action : Enregistrement ou Ignoré
            if faut_il_sauvegarder:
                print(f"🔴 [ENREGISTRÉ] t={temps_minutes:.2f} min | pH: {val_ph:.2f} | Temp: {val_temp:.2f}°C")
                
                # Écriture dans la base
                insert_row(
                    batch_id=BATCH_ID, temps=temps_minutes, pH=val_ph, 
                    temperature=val_temp, dissolved_oxygen=val_do, 
                    agitation=val_agit, aeration=val_aer
                )
                
                # Mise à jour de la mémoire avec les nouvelles valeurs
                derniere_ecriture["pH"] = val_ph
                derniere_ecriture["temperature"] = val_temp
                derniere_ecriture["dissolved_oxygen"] = val_do
                derniere_ecriture["agitation"] = val_agit
                derniere_ecriture["aeration"] = val_aer
            else:
                print(f"⚪ [IGNORÉ - Deadband] t={temps_minutes:.2f} min | Valeurs stables.")

            # 4. Attente avant la prochaine mesure
            await asyncio.sleep(INTERVAL)
            temps_ecoule_secondes += INTERVAL

    except Exception as e:
        print(f"❌ Erreur de communication avec le bioréacteur : {e}")
    finally:
        await client.disconnect()
        print("🔌 Déconnecté du bioréacteur.")

if __name__ == "__main__":
    asyncio.run(main())