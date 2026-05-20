import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def generate_report(diag, seuils, batch_name):
    """Génère un rapport PDF en mémoire et le renvoie pour le téléchargement."""
    # Création d'un buffer en mémoire (pas besoin de sauvegarder sur le disque)
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    
    # Dimensions de la page A4
    largeur, hauteur = A4
    
    # EN-TÊTE
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, hauteur - 50, "Rapport de Supervision - Bioprocess Monitor")
    
    c.setFont("Helvetica", 10)
    date_gen = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    c.drawString(50, hauteur - 70, f"Généré le : {date_gen}")
    c.line(50, hauteur - 80, largeur - 50, hauteur - 80) # Ligne de séparation
    
    # SECTION 1 : RÉSULTATS DU BATCH
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, hauteur - 120, f"1. Informations du Batch : {batch_name}")
    
    c.setFont("Helvetica", 11)
    statut = "ANORMAL (Alertes détectées)" if diag['taux_anomalie'] > 0 else "NOMINAL (Aucune alerte)"
    c.drawString(70, hauteur - 145, f"Statut global : {statut}")
    c.drawString(70, hauteur - 165, f"Taux d'anomalie : {diag['taux_anomalie']} %")
    c.drawString(70, hauteur - 185, f"Points de mesure analysés : {diag['nb_points_total']}")
    
    if diag["premier_instant"]:
        c.setFillColorRGB(0.8, 0, 0) # Texte en rouge pour l'alerte
        c.drawString(70, hauteur - 205, f"Première alerte à : t = {diag['premier_instant']} min")
        c.drawString(70, hauteur - 225, f"Capteurs impactés : {', '.join(diag['capteurs_touches'])}")
        c.setFillColorRGB(0, 0, 0) # Retour au noir
    
    # SECTION 2 : SEUILS DE TOLÉRANCE
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, hauteur - 270, "2. Paramètres de Tolérance (Seuils appliqués lors de l'analyse)")
    
    c.setFont("Helvetica", 11)
    c.drawString(70, hauteur - 295, f"pH : entre {seuils['pH'][0]} et {seuils['pH'][1]}")
    c.drawString(70, hauteur - 315, f"Température : entre {seuils['temperature'][0]} °C et {seuils['temperature'][1]} °C")
    c.drawString(70, hauteur - 335, f"Oxygène Dissous (DO) : entre {seuils['dissolved_oxygen'][0]} % et {seuils['dissolved_oxygen'][1]} %")
    
    # SECTION 3 : ESPACE SIGNATURE
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, hauteur - 420, "Visa / Signature du responsable :")
    c.line(50, hauteur - 460, 250, hauteur - 460) # Ligne pour signer
    
    # Bas de page
    c.setFont("Helvetica-Oblique", 9)
    c.drawString(50, 30, "Document généré automatiquement. Conforme aux exigences de traçabilité.")
    
    # Sauvegarde dans le buffer
    c.save()
    buffer.seek(0)
    return buffer.getvalue()