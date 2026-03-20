import os

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
FASTAPI_PORT = os.getenv("FASTAPI_PORT", "8000")
API_URL = f"http://mon_api:{FASTAPI_PORT}"
st.set_page_config(page_title="Iris Predictor", page_icon="🌸")

st.title("🌸 Classification des Iris")
st.write(
    "Entrez les caractéristiques de la fleur pour obtenir une prédiction en temps réel via l'API."
)

# 1. Formulaire de saisie
with st.sidebar:
    st.header("Paramètres de la fleur")
    sl = st.slider("Longueur Sépale (cm)", 4.0, 8.0, 5.1)
    sw = st.slider("Largeur Sépale (cm)", 2.0, 5.0, 3.5)
    pl = st.slider("Longueur Pétale (cm)", 1.0, 7.0, 1.4)
    pw = st.slider("Largeur Pétale (cm)", 0.1, 3.0, 0.2)

# 2. Bouton de prédiction
if st.button("Prédire l'espèce"):
    payload = {
        "sepal_length": sl,
        "sepal_width": sw,
        "petal_length": pl,
        "petal_width": pw,
    }

    try:
        # Appel à ton API FastAPI
        with st.spinner("Interrogation du modèle..."):
            response = requests.post(f"{API_URL}/predict", json=payload)
            response.raise_for_status()
            result = response.json()

        # 3. Affichage du résultat
        st.success(f"Résultat : **{result['prediction'].upper()}**")

        col1, col2 = st.columns(2)
        col1.metric("Version du modèle", result["model_version"])
        col2.metric("Index de classe", result["class_index"])

    except Exception as e:
        st.error(f"Erreur de connexion à l'API : {e}")
