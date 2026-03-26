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
git clone [https://github.com/Lionel-JOURDHIER/Prefect_MINIO](https://github.com/Lionel-JOURDHIER/Prefect_MINIO) && cd Prefect_MINIO
```

### 2. Préparation de l'environnement
Assurez-vous d'avoir **Docker Desktop** lancé et le gestionnaire de paquets **uv** installé.
vous allez avoir besoin de 2 terminaux : 
- Un terminal pour exécuter le serveur de training
- Un terminal pour exécuter les commandes de Docker.

```bash
(cd src/app_train && uv sync)
```

### 3. Création du réseau (Indispensable)
Avant de lancer les conteneurs, le réseau doit exister dans l'espace Docker :
```bash
docker network create --driver bridge --opt "com.docker.network.bridge.host_binding_ipv4"="127.0.0.1" monitoring-network
docker network create --driver bridge --opt "com.docker.network.bridge.host_binding_ipv4"="127.0.0.1" prefect-network
```
*Note : Si le réseau existe déjà, passez à l'étape suivante.*

### 4. Lancer le docker du serveur de training

```bash
(cd src/app_train && docker compose -f docker_compose.prefect.yml up --build -d)
```

### 5. Lancer le docker du serveur de l'API et de mlflow
```bash
docker compose build && docker compose up -d
```

### 6. Entrainement du premier modèle 
Si vous lancez l'application la première fois, il faurdra créer le premier modèle. 
Nous vous invitons donc à lancer donc à lancer la commande suivante : 
```bash
(cd src/app_train && uv run python train.py --init)
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

## Automatisation de la création de modèles avec prefect (cas de déploiement)
**Nota bene:** 
pour toute les commandes prefect, le venv de train doit être ouvert. 
```bash
source src/app_train/.venv/bin/activate
```
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
(cd src/app_train && prefect deploy --all)
```
#### Alternative sans déploiement: Lancement des worker en local avec la fonction serve
```bash
(cd src/app_train && uv run python train.py --serve)
```

### Démarage des workers
```bash
prefect worker start --pool 'train-pool'
```
#### Alternative : démarage des worker dans le fichier train.py
```bash
(cd src/app_train && uv run python train.py)
```

### Lancement d'une run sans attendre le scheduler de prefect
Vous pouvez lancer la run sans attendre le scheduler de prefect en ouvrant l'UI de Prefect : `http://localhost:4200` 
et en lançant une run de test depuis l'onglet Deployments.

#### Alternative : démarage de la run dans le fichier train.py
```bash
(cd src/app_train && uv run python train.py --run)
```

### Fermeture du docker prefect (Attention les workers sont en attente si le docker n'est pas down)
```bash
(cd src/app_train && docker compose -f docker_compose.prefect.yml down)
```

## Monitoring
### Commande pour lancer le monitoring : 
```bash
(cd monitoring && docker compose -f docker-compose.monitoring.yaml up -d)
```
### Prometheus
Prometheus agit comme le cœur du système de monitoring en servant de base de données orientée séries temporelles. 
Il est configuré pour "scrapper" (récupérer) activement les données de l'API FastAPI via son endpoint /metrics à intervalles réguliers. 
Sa puissance réside dans son langage de requête, le PromQL, qui permet d'agréger des données brutes en indicateurs métier pertinents.

Pour vérifier l'état de santé de vos cibles de collecte, l'interface native est accessible sur le port 9090. 
C'est ici que vous pouvez valider que l'API est bien détectée comme "UP" et tester vos premières requêtes sur les métriques personnalisées, 
comme le nombre total de requêtes ou les temps de latence de traitement des fichiers MinIO.

### Grafana
Grafana est l'outil de visualisation qui transforme les données brutes de Prometheus en tableaux de bord interactifs et lisibles. 
Grâce au système de provisioning automatique inclus dans ce projet, la source de données Prometheus est pré-configurée au démarrage, 
vous évitant ainsi toute manipulation manuelle répétitive dans l'interface graphique pour lier vos services.

L'interface est disponible sur le port 3000 avec les identifiants par défaut définis dans le fichier de configuration. 
Elle permet de créer des graphiques en temps réel pour surveiller l'utilisation des ressources système ou le flux de données passant par Streamlit, 
offrant ainsi une vue d'ensemble immédiate sur la stabilité de votre architecture de données.

### Uptime kuma
Uptime Kuma complète ce dispositif en se concentrant sur la disponibilité pure et simple de vos services (Uptime). 
Contrairement à Prometheus qui analyse les performances internes, Uptime Kuma vérifie de l'extérieur si vos interfaces Web et vos points d'accès API sont joignables, 
simulant ainsi l'expérience réelle d'un utilisateur final.

Cet outil propose une interface intuitive pour configurer des alertes immédiates en cas de coupure d'un service. 
Il permet de générer des pages de statut publiques ou privées, offrant un historique clair des temps d'arrêt, 
ce qui est essentiel pour maintenir un niveau de service élevé sur votre application de gestion de fichiers et de modèles ML.

## Vérification technique
Pour verifier que l'ensemble du projet est lancé, veuillez vous connecter aux adresses suivantes : 
|Nom du service|Adresse|Objectif|
|---|---|---|
|API|http://localhost:8000|Vérifiez que l'API est fonctionnelle|
|API (Swagger)|http://localhost:8000/docs||Vérifiez que la documentation interactive de l'API est accessible et fonctionnelle|
|Frontend Streamlit|http://localhost:8501|Vérifiez que la page Streamlit est accessible et fonctionnelle|
|MLFlow UI|http://localhost:5000|Vérifiez que le modèle est bien enregistré dans le Registry|
|MinIO Console|http://localhost:9001|Vérifiez la présence des artefacts dans le bucket mlflow.|
|Prefect UI|http://localhost:4200|Vérifiez que l'automatisation est bien déployée, que les workpools sont bien créés et possibilité de lancer des run de test depuis l'onglet Deployments|
|Prometheus|http://localhost:9090|Vérifiez que les métriques sont bien exposées et scrappées|
|Grafana|http://localhost:3000|Vérifiez que le dashboard est fonctionnel et affiche les métriques|
|Uptime Kuma|http://localhost:3001|Vérifiez que le service de monitoring est fonctionnel|


## 📂 Structure du Projet
```
.
├── data/               # Datasets (iris_test.csv)
├── src/
│   ├   ├── app_api/            # Backend FastAPI (logique de chargement MLflow)
│   │   │   ├── modules
│   │   │   │   ├── load_model.py         # Chargement des models depuis MINIO
│   │   │   │   └── modele_reg.py         # Préparation de MINIO - création automatique de bucket
│   │   │   ├── Dockerfile          # Dockerfile de l'API
│   │   │   ├── main.py             # Point d'entrée de l'API
│   │   │   ├── pyproject.toml      # Gestion des dépendances (uv)
│   │   │   ├── uv.lock             # Lockfile pour uv
│   │   │   └── README.md           # Readme de la partie API (TODO)
│   ├── app_front/          # Frontend Streamlit (interface utilisateur)
│   │   │   ├── services
│   │   │   │   └── Vide            # Services Streamlit selon besoin
│   │   │   ├── pages
│   │   │   │   └── Vide            # Pages Streamlit selon besoin
│   │   │   ├── Dockerfile          # Docker file du front
│   │   │   ├── app.py              # Point d'entrée du front
│   │   │   ├── pyproject.toml      # Gestion des dépendances (uv)
│   │   │   ├── uv.lock             # Lockfile pour uv
│   │   │   └── README.md           # Readme de la partie Front (TODO)
│   └── app_train/          # Scripts d'entraînement
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
| **fermer le docker prefect** | `(cd src/app_train && docker compose -f docker_compose.prefect.yml down)` |
| **fermer le docker monitorinng** | `(cd monitoring && docker compose -f docker-compose.monitoring.yaml down)` |

