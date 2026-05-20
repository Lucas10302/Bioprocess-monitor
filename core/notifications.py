import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "ton_email_labo@gmail.com"
SENDER_PASSWORD = "ton_mot_de_passe_application"

def send_email_alert(batch_id, capteurs_en_alerte, temps_alerte, destinataire):
    """Envoie un email d'urgence au responsable du batch."""
    sujet = f"🚨 ALERTE CRITIQUE - Bioréacteur {batch_id}"
    corps_message = f"""
    URGENCE BIOPROCESS MONITOR
    -----------------------------------
    Une anomalie a été détectée sur le batch : {batch_id}
    Temps de l'alerte : t = {temps_alerte} min
    Capteurs hors tolérance : {', '.join(capteurs_en_alerte)}
    
    Veuillez inspecter la cuve immédiatement.
    """
    
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = destinataire
    msg['Subject'] = sujet
    msg.attach(MIMEText(corps_message, 'plain'))
    
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"📧 Email d'alerte envoyé avec succès à {destinataire}")
        return True
    except Exception as e:
        print(f"❌ Échec de l'envoi de l'email : {e}")
        return False