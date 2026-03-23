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
- Un terminal pour exécuter le serveur de training
- Un terminal pour exécuter les commandes de Docker.

```bash
(cd src/train && uv sync)
```

### 3. Lancer le docker du serveur de training

```bash
(cd src/train && docker compose -f docker_compose.prefect.yml up --build -d)
```

### 4. Lancer le docker du serveur de l'API et de mlflow
```bash
docker compose build && docker compose up -d
```

### 5. Entrainement du premier modèle 
Si vous lancez l'application la première fois, il faurdra créer le premier modèle. 
Nous vous invitons donc à lancer donc à lancer la commande suivante : 
```bash
(cd src/train && uv run python train.py --init)
```
cette commande va : 
- aller dans le dossier d'entrainement, 
- lancer le flow d'entrainement pour prefect
- Retourner à la racine

Attention n'oubliez pas de lancer le server de training avant d'exécuter les commandes
Si vous ne souhaitez pas lancer le serveur via docker compose pour le lancement, 
vous pouvez uttiliser la commande suivante : 
```bash
prefect server start
```

## Automatisation de la création de modèles avec prefect

### Creation des workers
```bash
prefect work-pool create "train-pool" --type docker
```

### Limitation du nombre de worker si espace disque limité
```bash
prefect work-pool update --concurrency-limit 1 train-pool
```

### Deploiement suivant le fichier prefect.yaml
```bash
(cd src/train && prefect deploy --all)
```

### Démarage des workers
```bash
prefect worker start --pool 'train-pool'
```

- **Étape 2** : Vérification technique
Les adresses sont celle definis dans le fichier .env. Vous pouvez utiliser les adresses pour tester la fonctionnalité de prédiction.
* Prefect : http://localhost:4200 (Verification que l'automatisation est bien déployée, que les workpools sont bien créés et possibilité de lancer des run de test depuis l'onglet Deployments)
  
* MLflow UI : http://localhost:5000 (Vérifiez que le modèle est bien enregistré dans le Registry).

* MinIO Console : http://localhost:9001 (Vérifiez la présence des artefacts dans le bucket mlflow).

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
│   │   │   │   ├── def_model.py                # Définition du modèle
│   │   │   │   └── prep_data_iris.py           # Préparation des données Iris
│   │   │   ├── train.py                        # poitn d'entrée de l'entrainement des modèles
│   │   │   ├── Dockerfile                      # Creation de workers
│   │   │   ├── docker_compose.prefect.yml      # Docker compose pour l'utilisation de prefect
│   │   │   ├── prefect.yaml                    # Configuration de l'automation du flow
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


Commande pour lancer prefect
```bash
(cd src/train && docker compose -f docker_compose.prefect.yml up -d)
```