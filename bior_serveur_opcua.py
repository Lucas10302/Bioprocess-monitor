import asyncio
from asyncua import Server
import random

async def main():
    # Initialisation du serveur OPC-UA (ton faux bioréacteur)
    server = Server()
    await server.init()
    server.set_endpoint("opc.tcp://localhost:4840/freeopcua/server/")
    server.set_server_name("Bioréacteur Virtuel Labo")

    # Création de l'espace de noms (Namespace)
    idx = await server.register_namespace("http://bioprocess.labo.org")

    # Création du "dossier" contenant les capteurs
    obj = await server.nodes.objects.add_object(idx, "Capteurs_Bioreacteur")

    # On crée les nœuds pour les capteurs existants
    ph_node = await obj.add_variable(f"ns={idx};s=pH_Sensor", "pH_Sensor", 7.0)
    temp_node = await obj.add_variable(f"ns={idx};s=Temp_Sensor", "Temp_Sensor", 37.0)
    do_node = await obj.add_variable(f"ns={idx};s=DO_Sensor", "DO_Sensor", 100.0)
    
    # ─── NOUVEAUX CAPTEURS INDUSTRIELS ───
    agitation_node = await obj.add_variable(f"ns={idx};s=Agitation_Sensor", "Agitation_Sensor", 300.0)
    aeration_node = await obj.add_variable(f"ns={idx};s=Aeration_Sensor", "Aeration_Sensor", 1.5)

    # Rendre les capteurs "modifiables" par le serveur
    await ph_node.set_writable()
    await temp_node.set_writable()
    await do_node.set_writable()
    await agitation_node.set_writable()
    await aeration_node.set_writable()

    print("🟢 Bioréacteur virtuel démarré (OPC-UA) !")
    print("Adresse d'écoute : opc.tcp://localhost:4840/freeopcua/server/")
    print("Génération des données en cours... (Ctrl+C pour arrêter)")

    async with server:
        while True:
            await asyncio.sleep(2) # Mise à jour toutes les 2 secondes
            
            # Simulation de valeurs réalistes
            new_ph = 7.0 + random.uniform(-0.05, 0.05)
            new_temp = 37.0 + random.uniform(-0.1, 0.1)
            new_do = 35.0 + random.uniform(-1.0, 1.0)
            
            # ─── SIMULATION DE L'AGITATION & AÉRATION ───
            new_agitation = 300.0 + random.uniform(-5.0, 5.0)   # Autour de 300 rpm
            new_aeration = 1.5 + random.uniform(-0.05, 0.05)    # Autour de 1.5 L/min
            
            # Application des valeurs aux capteurs
            await ph_node.write_value(new_ph)
            await temp_node.write_value(new_temp)
            await do_node.write_value(new_do)
            await agitation_node.write_value(new_agitation)
            await aeration_node.write_value(new_aeration)

if __name__ == "__main__":
    asyncio.run(main())