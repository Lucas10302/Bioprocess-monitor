# 🧪 BioProcess Monitor

![Python](https://img.shields.io/badge/Python-3.10-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?logo=streamlit&logoColor=white)
![TimescaleDB](https://img.shields.io/badge/TimescaleDB-Database-FDB515?logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)

BioProcess Monitor is an end-to-end industrial software architecture for real-time acquisition, filtering, and supervision of metabolic data from bioreactors. Designed to meet Industry 4.0 requirements and the **21 CFR Part 11** standard.

## 🏗️ System Architecture

The project relies on 4 asynchronously operating pillars:
1. **OPC-UA Server (Simulation):** Emulates a bioreactor programmable logic controller (PLC) generating high-frequency data.
2. **IoT Connector & Deadband Filter:** A Python script that subscribes to the OPC-UA stream and applies a *Deadband* filter to prevent database overload.
3. **Time-Series Database:** A TimescaleDB instance (PostgreSQL optimized for time-series data) deployed via Docker.
4. **Analytical Supervisor:** A Streamlit Web interface offering kinetics visualization, real-time anomaly detection, and regulatory reporting.

## 🚀 Installation & Deployment (Docker)

The project is fully containerized. To launch the virtual control room:

1. Clone this repository:
   ```bash
   git clone [https://github.com/YOUR_NAME/bioprocess-monitor.git](https://github.com/YOUR_NAME/bioprocess-monitor.git)
   cd bioprocess-monitor
   Configure your environment variables:
2. Copy the .env.example file to .env and fill in your credentials.
3. Launch the Docker cluster: docker-compose up --build -d
4. Access the dashboard at http://localhost:8501.

## 🏭 Transition to a Real Bioreactor (Production)
This architecture was designed to transition from a simulation environment to a real physical production unit:

1. Network Connection: Replace the local simulator URL with the IP address of the real tank's PLC in opcua_connector.py: OPC_URL = "opc.tcp://192.168.10.50:4840"
2. Sensor Mapping (Node IDs): Modify the address dictionary to match the OPC-UA exchange table provided by the manufacturer: NODE_PH = "ns=4;i=10258"
NODE_DO = "ns=4;i=10259"
3. Access Security: Enable username/password authentication when initializing the client: client.set_user("plant_operator")
client.set_password("SecurePassword123!")
4. Colle ce texte dans ton nouveau fichier.
5. **Appuie sur `Ctrl + S` pour sauvegarder.** C'est crucial.
