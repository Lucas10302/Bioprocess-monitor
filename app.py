import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import sys
import os
import time
from datetime import datetime

# ==============================================================================
# 1. CONFIGURATION DE LA PAGE & THÉMATISATION (CYBER LAB)
# ==============================================================================
st.set_page_config(
    layout="wide", 
    page_title="BioProcess Monitor | Enterprise", 
    page_icon="🧪",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    h1, h2, h3 { color: #E2E8F0 !important; }
    .kpi-container { display: flex; gap: 15px; margin-bottom: 25px; }
    .kpi-card { background-color: #1F2633; border-radius: 10px; padding: 20px; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4); border-left: 5px solid #00E5FF; flex: 1; transition: transform 0.2s; }
    .kpi-card:hover { transform: translateY(-2px); }
    .kpi-title { color: #94A3B8; font-size: 12px; text-transform: uppercase; font-weight: bold; letter-spacing: 1px; }
    .kpi-value { color: #FFFFFF; font-size: 26px; font-weight: 700; margin-top: 5px; font-family: 'Courier New', Courier, monospace; }
    .kpi-card.alert { border-left: 5px solid #FF4B4B; background-color: #2D1E24; }
    </style>
""", unsafe_allow_html=True)

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.detector import detect_anomalies, generate_diagnostic
from core.report import generate_report
from core.database import fetch_batch, list_batches, log_audit_action, log_audit_event
from core.notifications import send_email_alert

SENSOR_COLS = {
    "pH": "Potentiel Hydrogène (pH)",
    "temperature": "Température (°C)",
    "dissolved_oxygen": "Oxygène Dissous (DO %)",
    "agitation": "Vitesse d'Agitation (RPM)",
    "aeration": "Débit d'Aération (L/min)"
}

COLORS = {
    "pH": "#00E5FF", "temperature": "#FF9100", "dissolved_oxygen": "#00E676", "agitation": "#D500F9", "aeration": "#FFEA00"
}

mapping_colonnes = {
    "ph": "pH", "do": "dissolved_oxygen", "DO": "dissolved_oxygen", "temperature": "temperature", "agitation": "agitation", "aeration": "aeration"
}

# ==============================================================================
# 2. AUTHENTIFICATION
# ==============================================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.title("🔒 Accès Restreint — BioProcess")
        user_input = st.text_input("Identifiant Chercheur / Opérateur")
        pwd_input = st.text_input("Mot de passe", type="password")
        if st.button("Se connecter", use_container_width=True):
            if pwd_input == "Labo2024" and user_input != "":
                st.session_state.logged_in = True
                st.session_state.username = user_input
                log_audit_action(user_input, "Connexion", "Accès accordé.")
                st.rerun()
            else:
                st.error("Identifiants incorrects.")
    st.stop()

# ==============================================================================
# 3. SIDEBAR & CHARGEMENT
# ==============================================================================
with st.sidebar:
    st.markdown(f"### 👤 Opérateur : `{st.session_state.username}`")
    if st.button("Se déconnecter", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()
        
    st.divider()
    st.title("⚙️ Contrôle Avancé")
    
    with st.form("form_seuils"):
        seuils = {
            "pH": (st.number_input("pH min", value=6.80), st.number_input("pH max", value=7.20)),
            "temperature": (st.number_input("Temp min", value=36.50), st.number_input("Temp max", value=37.50)),
            "dissolved_oxygen": (st.number_input("DO min", value=30.0), st.number_input("DO max", value=40.0)),
            "agitation": (st.number_input("Agit min", value=250.0), st.number_input("Agit max", value=350.0)),
            "aeration": (st.number_input("Aer min", value=1.0), st.number_input("Aer max", value=2.0))
        }
        if st.form_submit_button("🔒 Verrouiller Seuils"):
            st.success("Seuils validés.")
            
    refresh_rate = st.slider("Rafraîchissement (sec)", 1, 30, 3)

df_raw, df_ref, batch_name = None, None, "En attente..."

try:
    batches_historiques = list_batches()
    
    # 🛠️ Le Radar discret :
    with st.sidebar.expander("🛠️ Diagnostic Système"):
        st.write(f"URL: {os.getenv('DB_URL').split('@')[-1]}")
        st.write(f"Batches trouvés : {len(batches_historiques)}")

    if not batches_historiques.empty:
        batch_id = st.sidebar.selectbox("📍 Unité Mobile / Flux Actif", batches_historiques["batch_id"].tolist())
        df_raw = fetch_batch(batch_id).rename(columns=mapping_colonnes)
        batch_name = batch_id
    else:
        st.warning("⏳ En attente de connexion avec TimescaleDB (Aucun flux de données détecté)...")
        time.sleep(refresh_rate)
        st.rerun()
except Exception as e:
    st.error(f"Erreur DB: {e}")
    st.stop()

if df_raw is None or df_raw.empty:
    st.stop()

# ==============================================================================
# 4. ANALYSE ET UI 
# ==============================================================================
window = 10
df = detect_anomalies(df_raw, seuils, window=window)
diag = generate_diagnostic(df, seuils)

st.title("🧪 BioProcess Supervisor — Enterprise Edition")
st.divider()

# On vérifie s'il y a plus de 0 point anormal, ce qui évite le bug du "t = 0.0"
if diag.get("nb_points_anormaux", 0) > 0:
    st.error(f"🚨 **ALERTE CRITIQUE** — Anomalie détectée à partir de t = {diag['premier_instant']} min | Capteurs touchés : {', '.join(diag['capteurs_touches'])}", icon="⚠️")
else:
    st.success("✅ **STATUT OPÉRATIONNEL NOMINAL** — Toutes les constantes respectent les spécifications.", icon="🛡️")

cols_kpi = st.columns(5)
derniere_mesure = df.iloc[-1]
for idx, (col_id, label) in enumerate(SENSOR_COLS.items()):
    valeur = derniere_mesure[col_id]
    is_anormal = "alert" if (valeur < seuils[col_id][0] or valeur > seuils[col_id][1]) else ""
    unit = " RPM" if col_id == "agitation" else " L/min" if col_id == "aeration" else " °C" if col_id == "temperature" else " %" if col_id == "dissolved_oxygen" else ""
    with cols_kpi[idx]:
        st.markdown(f'<div class="kpi-card {is_anormal}"><div class="kpi-title">{label}</div><div class="kpi-value">{valeur:.2f}{unit}</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.subheader("📈 Courbes Cinétiques & Enveloppes de Tolérances")

def draw_cyber_chart(df_data, param, label, color, range_seuils):
    fig = go.Figure()
    
    # 1. La courbe principale (Ligne lissée)
    fig.add_trace(go.Scatter(
        x=df_data["temps"], 
        y=df_data[param], 
        mode="lines", 
        line=dict(color=color, width=3, shape='spline')
    ))
    
    # 2. 🚨 LE RETOUR DES ANOMALIES : Dessine un point rouge fluo pour chaque déviance
    anom_col = f"anomalie_{param}"
    if anom_col in df_data.columns:
        df_anom = df_data[df_data[anom_col]]
        if not df_anom.empty:
            fig.add_trace(go.Scatter(
                x=df_anom["temps"], 
                y=df_anom[param], 
                mode="markers", 
                name="Incongruence",
                marker=dict(color="#FF4B4B", size=8, symbol="circle", line=dict(color="#FFFFFF", width=1))
            ))
    
    # 3. La zone de tolérance verte transparente
    fig.add_hrect(
        y0=range_seuils[0], y1=range_seuils[1], 
        fillcolor="#10B981", opacity=0.04, line_width=0
    )
    
    # 4. Le design global avec auto-zoom
    fig.update_layout(
        title=dict(text=label, font=dict(color="#FFFFFF", size=14)), 
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)', 
        margin=dict(l=40, r=20, t=40, b=30), 
        height=240, 
        showlegend=False,
        xaxis=dict(gridcolor="#222938", color="#94A3B8"), 
        yaxis=dict(gridcolor="#222938", color="#94A3B8", autorange=True) 
    )
    return fig

graph_cols = st.columns(2)
with graph_cols[0]:
    st.plotly_chart(draw_cyber_chart(df, "pH", "Potentiel Hydrogène (pH)", "rgba(0, 229, 255, 1)", seuils["pH"]), use_container_width=True)
    st.plotly_chart(draw_cyber_chart(df, "dissolved_oxygen", "Oxygène Dissous (DO %)", "rgba(0, 230, 118, 1)", seuils["dissolved_oxygen"]), use_container_width=True)
with graph_cols[1]:
    st.plotly_chart(draw_cyber_chart(df, "temperature", "Température (°C)", "rgba(255, 145, 0, 1)", seuils["temperature"]), use_container_width=True)
    st.plotly_chart(draw_cyber_chart(df, "agitation", "Agitation (RPM)", "rgba(213, 0, 249, 1)", seuils["agitation"]), use_container_width=True)

st.plotly_chart(draw_cyber_chart(df, "aeration", "Aération (L/min)", "rgba(255, 234, 0, 1)", seuils["aeration"]), use_container_width=True)

st.divider()

# ==============================================================================
# 5. MODULES DE REPORTING RÈGLEMENTAIRE ET DE TÉLÉCHARGEMENT PDF
# ==============================================================================
cols_bas = st.columns([1, 1])

with cols_bas[0]:
    st.subheader("📄 Reporting Règlementaire (21 CFR)")
    diag["nb_points_total"] = len(df)
    
    # Compilation dynamique du buffer PDF
    pdf_buffer = generate_report(diag, seuils, batch_name=batch_name)
    
    st.download_button(
        label="⬇️ Compiler et Exporter le rapport d'analyse signé (PDF)",
        data=pdf_buffer,
        file_name=f"Rapport_Conformite_{batch_name}_{datetime.now().strftime('%Y%m%d')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )

with cols_bas[1]:
    if diag.get("nb_points_anormaux", 0) > 0:
        with st.expander("🔍 Extraire le log brut des déviances"):
            cols_show = [c for c in ["temps", "pH", "temperature", "dissolved_oxygen", "agitation", "aeration"] if c in df.columns]
            st.dataframe(df[df["anomalie_globale"]][cols_show].round(3), use_container_width=True)

# Écoute et boucle de rafraîchissement automatique
time.sleep(refresh_rate)
st.rerun()