# 🧪 BioProcess Monitor

![Python](https://img.shields.io/badge/Python-3.10-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?logo=streamlit&logoColor=white)
![TimescaleDB](https://img.shields.io/badge/TimescaleDB-Database-FDB515?logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)

BioProcess Monitor est une architecture logicielle industrielle de bout-en-bout permettant l'acquisition, le filtrage et la supervision en temps réel des données métaboliques de bioréacteurs. Conçu pour répondre aux exigences de l'industrie 4.0 et à la norme **21 CFR Part 11**.

## 🏗️ Architecture du Système

Le projet repose sur 4 piliers fonctionnant de manière asynchrone :
1. **Serveur OPC-UA (Simulation) :** Émule un automate programmable (PLC) de bioréacteur générant des données à haute fréquence.
2. **Connecteur IoT & Filtre Deadband :** Un script Python qui s'abonne au flux OPC-UA et applique un filtre de *Deadband* pour éviter la surcharge de la base de données.
3. **Base de Données Temporelle :** Une instance `TimescaleDB` (PostgreSQL optimisé pour les séries temporelles) déployée via Docker.
4. **Superviseur Analytique :** Une interface Web `Streamlit` offrant une visualisation des cinétiques, la détection d'anomalies en temps réel, et un reporting règlementaire.

## ✨ Fonctionnalités Principales
* 📡 **Acquisition OPC-UA** : Standard mondial de communication industrielle.
* 🎛️ **Filtrage Intelligent (Deadband)** : Enregistrement conditionnel basé sur la variance des capteurs.
* 🚨 **Système d'Alerte** : Détection de dépassement de seuil et envoi automatique d'alertes par email.
* 📄 **Conformité 21 CFR Part 11** : Audit trail, authentification opérateur et génération de rapports de lots (Batch Reports) signés au format PDF.

## 🚀 Installation & Déploiement (Docker)

Le projet est entièrement conteneurisé. Pour lancer la salle de contrôle virtuelle :

1. Clonez ce dépôt :
   ```bash
   git clone [https://github.com/VOTRE_NOM/bioprocess-monitor.git](https://github.com/VOTRE_NOM/bioprocess-monitor.git)
   cd bioprocess-monitor

## 🏭 Transition vers un Bioréacteur Réel (Production)

Cette architecture a été conçue pour passer d'un environnement de simulation à une véritable unité de production physique (ex: Sartorius, Applikon, Eppendorf) avec un minimum de modifications :

1. **Raccordement Réseau :** Remplacer l'URL du simulateur local par l'adresse IP de l'automate (PLC) de la vraie cuve dans `opcua_connector.py` :
   ```python
   # Simulation : 
   # OPC_URL = "opc.tcp://localhost:4840/freeopcua/server/"
   
   # Production : 
   OPC_URL = "opc.tcp://192.168.10.50:4840" # Mettre l'IP physique de la machine

2. **Cartographie des Capteurs (Node IDs) :** Modifier le dictionnaire d'adresses pour correspondre à la table d'échange OPC-UA fournie par le constructeur de votre bioréacteur :
   # Simulation :
   # NODE_PH = "ns=2;s=pH_Sensor"

   # Production (Exemple pour une cuve industrielle) :
   NODE_PH = "ns=4;i=10258"
   NODE_DO = "ns=4;i=10259"
   
3. **Sécurisation des Accès :** Les équipements industriels exigeant souvent une sécurité stricte, il suffit d'activer l'authentification par certificat numérique ou par couple identifiant/mot de passe au moment de l'initialisation du client dans opcua_connector.py :
   client.set_user("operateur_usine")
   client.set_password("MotDePasseSecurise123!")
