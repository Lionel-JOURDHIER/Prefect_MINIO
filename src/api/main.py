import os

import pandas as pd
import psutil
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from loguru import logger
from modules.load_model import load_production_model
from modules.modele_reg import prepare_minio
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    Counter,
    Gauge,
    generate_latest,
)
from pydantic import BaseModel
from starlette.responses import Response

load_dotenv()

app = FastAPI(title="Iris Prediction API")

# si problème dans les metrics de prometheus, on peut désenregistrer le registre
# for collector in list(REGISTRY._collector_to_names.keys()):
#     REGISTRY.unregister(collector)


# Monitoring
my_registry = CollectorRegistry()

REQUEST_COUNT = Counter(
    "app_requests_total", "Total requests", ["method", "endpoint"], registry=my_registry
)
CPU_USAGE = Gauge("system_cpu_usage", "Usage CPU", registry=my_registry)

logger.add("/logs/fastapi.log", rotation="500 MB")


# Définition du format d'entrée (les 4 mesures de la fleur)
class IrisInput(BaseModel):
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float


@app.post("/predict")
async def predict(data: IrisInput):
    # 1. Charger le modèle (utilise le cache ou recharge si nécessaire)
    logger.info(f"Donnée reçue : {data}")
    REQUEST_COUNT.labels(method="POST", endpoint="/predict").inc()
    model, version = load_production_model()

    if model is None:
        raise HTTPException(status_code=500, detail="Le modèle n'a pas pu être chargé.")

    # 2. Préparer les données pour le modèle (format DataFrame souvent requis par sklearn)
    input_df = pd.DataFrame(
        [data.model_dump().values()],
        columns=[
            "sepal length (cm)",
            "sepal width (cm)",
            "petal length (cm)",
            "petal width (cm)",
        ],
    )

    try:
        # 3. Prédiction
        prediction = model.predict(input_df)

        # 4. Traduction du résultat (0, 1, 2) en nom de fleur
        target_names = ["setosa", "versicolor", "virginica"]
        predicted_class = target_names[int(prediction[0])]

        return {
            "prediction": predicted_class,
            "class_index": int(prediction[0]),
            "model_version": version,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erreur lors de la prédiction: {str(e)}"
        )


# @app.post("/predict")
# async def predict(data: IrisInput):
#     # Simule une réponse sans appeler MLflow pour vérifier que Streamlit s'affiche
#     return {
#         "prediction": "setosa (TEST MODE)",
#         "class_index": 0,
#         "model_version": "0.0.0-draft",
#     }


@app.get("/")
async def root():
    REQUEST_COUNT.labels(method="GET", endpoint="/").inc()
    return {"status": "API is alive"}


@app.get("/metrics")
async def metrics():
    CPU_USAGE.set(psutil.cpu_percent())
    return Response(generate_latest(my_registry), media_type=CONTENT_TYPE_LATEST)


@app.get("/health")
async def health_check():
    logger.debug("get sur route health sonde uptime kuma")
    return {"status": "OK", "message": "API is running"}


if __name__ == "__main__":
    prepare_minio()

    port_env = os.getenv("FASTAPI_PORT", "8000")
    host_url = "0.0.0.0"
    try:
        port = int(port_env)
    except (ValueError, TypeError):
        port = 8000
    uvicorn.run("main:app", host=host_url, port=port, log_level="debug")
