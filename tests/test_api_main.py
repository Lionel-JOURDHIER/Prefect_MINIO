from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


# 1. TEST : Route Racine
def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "API is alive"}


# 2. TEST : Health Check
def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "OK"


# 3. TEST : Metrics (Vérifie si Prometheus répond)
def test_metrics():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "system_cpu_usage" in response.text


# 4. TEST : Prédiction (Succès)
@patch("main.load_production_model")
def test_predict_success(mock_load):
    # On mocke le modèle pour qu'il renvoie une prédiction
    mock_model = MagicMock()
    mock_model.predict.return_value = [0]  # 0 = setosa
    mock_load.return_value = (mock_model, "1.0")

    payload = {
        "sepal_length": 5.1,
        "sepal_width": 3.5,
        "petal_length": 1.4,
        "petal_width": 0.2,
    }
    response = client.post("/predict", json=payload)

    assert response.status_code == 200
    assert response.json()["prediction"] == "setosa"
    assert response.json()["model_version"] == "1.0"


# 5. TEST : Erreur de chargement de modèle (Ligne 116)
@patch("main.load_production_model")
def test_predict_no_model(mock_load):
    mock_load.return_value = (None, None)

    payload = {"sepal_length": 0, "sepal_width": 0, "petal_length": 0, "petal_width": 0}
    response = client.post("/predict", json=payload)
    assert response.status_code == 500
    assert "Le modèle n'a pas pu être chargé" in response.json()["detail"]


# 6. TEST : Erreur lors de la prédiction (Ligne 138)
@patch("main.load_production_model")
def test_predict_error_during_inference(mock_load):
    mock_model = MagicMock()
    mock_model.predict.side_effect = Exception("Inference Crash")
    mock_load.return_value = (mock_model, "1.0")

    response = client.post(
        "/predict",
        json={"sepal_length": 1, "sepal_width": 1, "petal_length": 1, "petal_width": 1},
    )
    assert response.status_code == 500
    assert "Erreur lors de la prédiction" in response.json()["detail"]


def test_middleware_error_handling():
    """Force une erreur pour couvrir la branche 'except' du middleware"""
    # On patche une fonction appelée par la route /health pour qu'elle crashe
    with patch(
        "main.logger.debug", side_effect=RuntimeError("Middleware Trigger Test")
    ):
        with pytest.raises(RuntimeError):
            client.get("/health")
