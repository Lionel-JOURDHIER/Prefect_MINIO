# 🌸 Iris MLOps Factory

Ce projet est une plateforme de Machine Learning industrialisée utilisant une architecture micro-services. Elle permet de gérer le cycle de vie complet d'un modèle : de l'entraînement au suivi des métriques jusqu'à l'exposition via une API et une interface utilisateur.

---

## Architecture du Système

L'infrastructure est entièrement conteneurisée avec **Docker Compose** et s'articule autour de 4 composants clés :

1.  **MLflow Server** : Centralise le tracking des expériences (paramètres, métriques) et le registre des modèles (*Model Registry*).
2.  **MinIO (S3-Compatible)** : Sert de stockage d'objets (Object Storage) pour conserver les fichiers binaires des modèles (`.pkl`, `conda.yaml`).
3.  **FastAPI** : Le backend de prédiction. Il communique avec MLflow pour charger la version marquée comme "production" et expose une route `POST /predict`.
4.  **Streamlit** : L'interface utilisateur interactive pour saisir des données manuellement ou charger des exemples depuis un dataset de test.

---

## Installation et Démarrage
### 1.Clonage du projet : 
```bash
git clone [https://github.com/Lionel-JOURDHIER/MINIO_.git](https://github.com/Lionel-JOURDHIER/MINIO_.git) && cd MINIO_
```

### 2. Préparation de l'environnement
Assurez-vous d'avoir **Docker Desktop** lancé et le gestionnaire de paquets **uv** installé.
vous allez avoir besoin de 2 terminaux : 
- Un terminal pour exécuter les commandes d'entrainement
- Un terminal pour exécuter les commandes de Docker.

```bash
(cd src/train && uv sync)
```

### 3. Lancer Docker
```bash
docker compose build && docker compose up -d
```

### 4. Entrainement du premier modèle 
Attention si c'est la première fois que vous lancez le contener minio, aucun modèle n'est présent, il faut absoluement faire un entrainement avant de lancer l'application.
```bash
(cd src/train && uv run python train.py)
```

## Cycle de Vie du Modèle
- **Étape 1** : Entraînement et Enregistrement
Lancez l'entraînement depuis votre terminal hôte. Le script entraîne un modèle Random Forest, logue les métriques (accuracy) sur MLflow et upload le modèle vers MinIO.
```bash
(cd src/train && uv run python train.py)
```

- **Étape 2** : Vérification technique
Les adresses sont celle definis dans le fichier .env. Vous pouvez utiliser les adresses pour tester la fonctionnalité de prédiction.

MLflow UI : http://localhost:5000 (Vérifiez que le modèle est bien enregistré dans le Registry).

MinIO Console : http://localhost:9001 (Vérifiez la présence des artefacts dans le bucket mlflow).

- **Étape 3** : Prédiction
API (Swagger) : http://localhost:8000/docs

Frontend Streamlit : http://localhost:8501

## 📂 Structure du Projet
```
.
├── data/               # Datasets (iris_test.csv)
├── src/
│   ├   ├── api/            # Backend FastAPI (logique de chargement MLflow)
│   │   │   ├── modules
│   │   │   │   ├── load_model.py         # Chargement des models depuis MINIO
│   │   │   │   └── modele_reg.py         # Préparation de MINIO - création automatique de bucket
│   │   │   ├── Dockerfile          # Dockerfile de l'API
│   │   │   ├── main.py             # Point d'entrée de l'API
│   │   │   ├── pyproject.toml      # Gestion des dépendances (uv)
│   │   │   ├── uv.lock             # Lockfile pour uv
│   │   │   └── README.md           # Readme de la partie API (TODO)
│   ├── front/          # Frontend Streamlit (interface utilisateur)
│   │   │   ├── services
│   │   │   │   └── Vide            # Services Streamlit selon besoin
│   │   │   ├── pages
│   │   │   │   └── Vide            # Pages Streamlit selon besoin
│   │   │   ├── Dockerfile          # Docker file du front
│   │   │   ├── app.py              # Point d'entrée du front
│   │   │   ├── pyproject.toml      # Gestion des dépendances (uv)
│   │   │   ├── uv.lock             # Lockfile pour uv
│   │   │   └── README.md           # Readme de la partie Front (TODO)
│   └── train/          # Scripts d'entraînement
│   │   │   ├── services
│   │   │   │   ├── __init__.py     
│   │   │   │   ├── def_model.py          # Définition du modèle
│   │   │   │   └── prep_data_iris.py     # Préparation des données Iris
│   │   │   ├── train.py              # Point d'entrée du front
│   │   │   ├── pyproject.toml      # Gestion des dépendances (uv)
│   │   │   ├── uv.lock             # Lockfile pour uv
│   │   │   └── README.md           # Readme de la partie entrainement (TODO)
├── docker-compose.yml  # Orchestration des conteneurs
├── README.md           # Readme de l'orchestration et de l'utilisation de l'APP
└── .env                # Variables d'environnement (Secrets S3/API)
```

### Configuration 
#### Variables d'environnement (TODO)

Le projet utilise des variables d'environnement pour permettre la communication entre les différents services (micro-services).

| Variable | Usage / Description | Valeur Docker (Interne) |
| :--- | :--- | :--- |
| **AWS_ACCESS_KEY_ID** | Identifiant de connexion à MinIO | `exemple` |
| **AWS_SECRET_ACCESS_KEY** | Mot de passe de connexion à MinIO | `exemple` |
| **MLFLOW_S3_ENDPOINT_URL** | Point d'accès pour le stockage des modèles | `http://minio:9000` |
| **MLFLOW_TRACKING_URI** | URL du serveur de tracking MLflow | `http://mlflow:5000` |
| **STREAMLIT_API_URL** | Point d'entrée de l'API pour le Frontend | `http://api:9090` |

### Configuration de Docker Compose :
- Mise en garde pour la configuration du docker compose de mlflow : 
Bien mettre les allowed-hosts à jour pour permettre l'accès à votre application depuis le conteneur Docker.
```yaml
      mlflow server
      --backend-store-uri sqlite:////database/mlflow.db
      --default-artifact-root s3://mlflow/
      --host 0.0.0.0
      --dev
      --allowed-hosts "mlflow:*, localhost:*, minio:*" 
```

- Creation des volumes dans docker-compose.yml partie mlflow pour retrouver les models après un compose down. 
```yaml
    volumes:
      - ./mlflow_data:/database
```

### Commandes Utiles

| Action | Commande |
| :--- | :--- |
| **Démarrer les services** | `docker compose up -d` |
| **Forcer la reconstruction** | `docker compose up --build` |
| **Voir les logs de l'API** | `docker logs -f mon_api` |
| **Supprimer les données (volumes)** | `docker compose down -v` |
| **Vérifier l'état des conteneurs** | `docker compose ps` |
| **Supprimer les images / REGULIEREMENT** | `docker image prune -a` |
