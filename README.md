🧪 BioProcess Monitor — Enterprise Edition
BioProcess Monitor is an end-to-end industrial software architecture for real-time acquisition, filtering, and supervision of metabolic data from bioreactors. Designed to meet Industry 4.0 requirements and the 21 CFR Part 11 standard.

🏗️ System Architecture
The project relies on 4 asynchronously operating pillars:

OPC-UA Server (Simulation): Emulates a bioreactor programmable logic controller (PLC) generating high-frequency data.

IoT Connector & Deadband Filter: A Python script that subscribes to the OPC-UA stream and applies a Deadband filter to prevent database overload.

Time-Series Database: A TimescaleDB instance (PostgreSQL optimized for time-series data) deployed via Docker.

Analytical Supervisor: A Streamlit Web interface offering kinetics visualization, real-time anomaly detection, and regulatory reporting.

🚀 Installation & Deployment (Docker)
The project is fully containerized. To launch the virtual control room:

Clone this repository:
git clone https://github.com/YOUR_NAME/bioprocess-monitor.git
cd bioprocess-monitor

Configure your environment variables:
Copy the .env.example file to .env and fill in your credentials.

Launch the Docker cluster:
docker-compose up --build -d

Access the dashboard at http://localhost:8501.

🏭 Transition to a Real Bioreactor (Production)
This architecture was designed to transition from a simulation environment to a real physical production unit (e.g., Sartorius, Applikon, Eppendorf):

Network Connection: Replace the local simulator URL with the IP address of the real tank's PLC in opcua_connector.py:
OPC_URL = "opc.tcp://192.168.10.50:4840"

Sensor Mapping (Node IDs): Modify the address dictionary to match the OPC-UA exchange table provided by the manufacturer:
NODE_PH = "ns=4;i=10258"
NODE_DO = "ns=4;i=10259"

Access Security: Enable username/password authentication when initializing the client:
client.set_user("plant_operator")
client.set_password("SecurePassword123!")

Une fois que tu as collé ça dans ton fichier README.md et sauvegardé avec Ctrl + S, il te suffira de taper les 3 commandes dans ton terminal VS Code (en appuyant sur Entrée à chaque fois) pour forcer la mise à jour et écraser le conflit :

git add README.md

git commit -m "Update README to English version"

git push -u origin main -f
