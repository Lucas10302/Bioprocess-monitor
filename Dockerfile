# 1. On part d'une version de Python légère et officielle
FROM python:3.10-slim

# 2. On définit le dossier de travail dans le conteneur
WORKDIR /app

# 3. On copie le fichier des dépendances et on les installe
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. On copie tout le reste de ton code dans le conteneur
COPY . .

# 5. On indique le port utilisé par Streamlit
EXPOSE 8501

# 6. La commande pour démarrer l'application automatiquement
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]