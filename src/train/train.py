import os

import mlflow
import requests
from dotenv import load_dotenv
from mlflow import sklearn
from mlflow.tracking import MlflowClient
from services.def_model import model, params
from services.prep_data_iris import prepare_data
from sklearn.metrics import (
    accuracy_score,
)

load_dotenv()
TRACKING_URI = "http://localhost:5000"
S3_ENDPOINT = "http://localhost:9000"
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
MLFLOW_PORT = os.getenv("MLFLOW_PORT", "5000")
MINIO_PORT_S3 = os.getenv("MINIO_PORT_S3", "9000")
os.environ["MLFLOW_S3_IGNORE_TLS"] = "true"
os.environ["MLFLOW_TRACKING_URI"] = "http://localhost:5000"
os.environ["MLFLOW_S3_ENDPOINT_URL"] = "http://localhost:9000"


def train_and_register(model, X_train, y_train, X_test, y_test, params):
    # Configuration du serveur de tracking
    mlflow.set_tracking_uri(TRACKING_URI)
    mlflow.set_experiment("My_Experiment")
    # Chargement des données train/test

    with mlflow.start_run():
        # Entraînement
        model.fit(X_train, y_train)
        # Log des paramètres et metrics
        mlflow.log_params(params)
        y_pred = model.predict(X_test)

        # Evaluation du model
        accscore = accuracy_score(y_test, y_pred)
        metrics = {
            "accuracy": float(accscore),
        }
        mlflow.log_metrics(metrics)
        # 2. Enregistrement dans MinIO ET dans le Model Registry
        # On définit le nom du modèle dans le catalogue
        model_name = "model_name"
        sklearn.log_model(
            sk_model=model, artifact_path="model", registered_model_name=model_name
        )
    # 3. Gestion de l'Alias 'Production' via MlflowClient
    client = MlflowClient()

    # On récupère la toute dernière version créée
    latest_version = client.get_latest_versions(model_name, stages=["None"])[0].version

    # On lui attribue l'alias 'Production'
    client.set_registered_model_alias(model_name, "Production", latest_version)
    return model


if __name__ == "__main__":
    # Test de connexion
    try:
        requests.get("http://localhost:5000")
        print("✅ Serveur MLflow accessible !")
    except Exception:
        print("❌ Erreur : Le serveur http://localhost:5000 est injoignable.")
        exit(1)
    X_train, X_test, y_train, y_test = prepare_data()
    model = train_and_register(model, X_train, y_train, X_test, y_test, params)
