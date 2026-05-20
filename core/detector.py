import pandas as pd

def detect_anomalies(df, seuils, window=10):
    """
    Détecte les anomalies dans un DataFrame de données capteurs.

    Paramètres :
    - df      : DataFrame avec les colonnes capteurs
    - seuils  : dictionnaire {colonne: (min, max)}
    - window  : taille de la fenêtre de lissage (rolling mean)

    Retourne le DataFrame enrichi avec les colonnes d'anomalies.
    """
    df = df.copy()

    for colonne, (seuil_min, seuil_max) in seuils.items():
        if colonne not in df.columns:
            continue

        # Lissage du signal
        col_lisse = f"{colonne}_lisse"
        df[col_lisse] = df[colonne].rolling(window=window).mean()

        # Détection brute
        df[f"anomalie_{colonne}_brute"] = (
            (df[colonne] < seuil_min) | (df[colonne] > seuil_max)
        )

        # Détection robuste (sur signal lissé)
        df[f"anomalie_{colonne}"] = (
            (df[col_lisse] < seuil_min) | (df[col_lisse] > seuil_max)
        )

    # Anomalie globale
    cols_anomalie = [c for c in df.columns if c.startswith("anomalie_")
                     and not c.endswith("_brute")]
    df["anomalie_globale"] = df[cols_anomalie].any(axis=1)

    return df


def generate_diagnostic(df, seuils):
    """
    Génère un rapport de diagnostic sur le batch analysé.

    Retourne un dictionnaire avec :
    - premier_instant    : valeur temps de la première anomalie
    - capteurs_touches   : liste des capteurs en anomalie
    - nb_points_anormaux : nombre total de points anormaux
    - taux_anomalie      : pourcentage de points anormaux
    """
    df_clean = df.dropna()

    diagnostic = {
        "premier_instant"    : None,
        "capteurs_touches"   : [],
        "nb_points_anormaux" : int(df_clean["anomalie_globale"].sum()),
        "taux_anomalie"      : round(df_clean["anomalie_globale"].mean() * 100, 2)
    }

    # Premier instant anormal — on prend la valeur de la colonne temps
    anomalies = df_clean[df_clean["anomalie_globale"]]
    if not anomalies.empty:
        diagnostic["premier_instant"] = int(anomalies["temps"].iloc[0])

    # Capteurs touchés
    for colonne in seuils.keys():
        col = f"anomalie_{colonne}"
        if col in df_clean.columns and df_clean[col].any():
            diagnostic["capteurs_touches"].append(colonne)

    return diagnostic