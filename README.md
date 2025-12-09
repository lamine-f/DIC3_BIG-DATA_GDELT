# Atelier 1 : Cluster Spark avec Docker - Analyse GDELT

Mise en place d'un cluster Apache Spark local avec Docker pour analyser les événements GDELT et compter les événements par pays.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Docker Network                         │
│                       (spark-net)                           │
│                                                             │
│  ┌─────────────────┐         ┌─────────────────┐           │
│  │  Spark Master   │◄───────►│  Spark Worker   │           │
│  │                 │         │                 │           │
│  │  Port: 7077     │         │  Memory: 2G     │           │
│  │  UI: 8080       │         │  Cores: 2       │           │
│  │  App UI: 4040   │         │  UI: 8081       │           │
│  └─────────────────┘         └─────────────────┘           │
│           │                          │                      │
│           └──────────┬───────────────┘                      │
│                      │                                      │
│              ┌───────▼───────┐                              │
│              │   Volumes     │                              │
│              │  - /data      │                              │
│              │  - /app       │                              │
│              │  - /output    │                              │
│              └───────────────┘                              │
└─────────────────────────────────────────────────────────────┘
```

## Prérequis

- Docker Desktop installé et en cours d'exécution
- Docker Compose (inclus avec Docker Desktop)
- Minimum 4 Go de RAM disponible

## Structure du projet

```
Atelier 1/
├── docker-compose.yml      # Configuration du cluster Spark
├── event_counter.py        # Programme PySpark d'analyse
├── README.md               # Documentation (ce fichier)
├── datas/
│   └── 20251208.export.CSV # Données GDELT (111,373 événements)
└── output/
    └── event_counts_by_country/  # Résultats CSV générés
        └── part-00000-*.csv
```

## Installation et démarrage

### 1. Cloner ou télécharger le projet

Placez-vous dans le répertoire du projet :
```bash
cd "Atelier 1"
```

### 2. Télécharger les données GDELT (si nécessaire)

Les données GDELT peuvent être téléchargées depuis :
- http://data.gdeltproject.org/events/index.html

Placez le fichier `.CSV` dans le dossier `datas/`.

### 3. Démarrer le cluster Spark

```bash
docker-compose up -d
```

Cette commande :
- Télécharge l'image Apache Spark 3.5.0 (première exécution uniquement)
- Démarre le Spark Master
- Démarre le Spark Worker
- Configure le réseau entre les conteneurs

### 4. Vérifier que le cluster est opérationnel

```bash
docker ps
```

Vous devriez voir :
```
NAMES           STATUS          PORTS
spark-master    Up X minutes    0.0.0.0:7077->7077, 0.0.0.0:8080->8080
spark-worker-1  Up X minutes    0.0.0.0:8081->8081
```

## Utilisation

### Exécuter le job PySpark

#### Sur Windows (Git Bash ou PowerShell) :
```bash
docker exec spark-master //opt/spark/bin/spark-submit --master spark://spark-master:7077 //app/event_counter.py
```

#### Sur Linux/Mac :
```bash
docker exec spark-master /opt/spark/bin/spark-submit --master spark://spark-master:7077 /app/event_counter.py
```

### Sortie attendue

```
============================================================
GDELT Event Counter - Comptage des événements par pays
============================================================

Lecture des données depuis: /data/20251208.export.CSV
Nombre total d'événements chargés: 111373

============================================================
TOP 30 des pays par nombre d'événements:
============================================================
+------------------------------------------------+----------+
|CountryCode                                     |EventCount|
+------------------------------------------------+----------+
|Washington, District of Columbia, United States |2299      |
|Gaza, Israel (general), Israel                  |2094      |
|United States                                   |1972      |
|New York, United States                         |1562      |
|London, London, City of, United Kingdom         |1540      |
...
```

## Résultats

Les résultats sont sauvegardés dans le dossier `output/event_counts_by_country/` au format CSV :

```csv
CountryCode,EventCount
"Washington, District of Columbia, United States",2299
"Gaza, Israel (general), Israel",2094
United States,1972
"New York, United States",1562
...
```

### Lire les résultats

```bash
# Afficher les 20 premières lignes
head -20 output/event_counts_by_country/part-00000-*.csv
```

## Interfaces Web

| Interface | URL | Description |
|-----------|-----|-------------|
| Spark Master UI | http://localhost:8080 | État du cluster, workers connectés |
| Spark Worker UI | http://localhost:8081 | Détails du worker, exécutions |
| Spark Application UI | http://localhost:4040 | Jobs en cours, stages, DAG |

> Note : L'interface Application UI (4040) n'est disponible que pendant l'exécution d'un job.

## Données GDELT

### Format des fichiers

- **Format** : CSV avec séparateur tabulation (`\t`)
- **En-tête** : Non (les fichiers GDELT n'ont pas d'en-tête)
- **Encodage** : UTF-8

### Colonne utilisée

Le programme utilise la **colonne 51** (index 50) qui correspond au champ `ActionGeo_FullName` dans le schéma GDELT 2.0 Events. Ce champ contient le nom complet de la localisation géographique de l'événement.

### Schéma GDELT 2.0 (colonnes principales)

| Index | Nom | Description |
|-------|-----|-------------|
| 0 | GlobalEventID | Identifiant unique de l'événement |
| 1 | Day | Date au format YYYYMMDD |
| 5 | Actor1Code | Code de l'acteur 1 |
| 15 | Actor2Code | Code de l'acteur 2 |
| 50 | ActionGeo_FullName | Localisation complète de l'action |
| 57 | SOURCEURL | URL de la source |

## Arrêt du cluster

### Arrêter les conteneurs
```bash
docker-compose down
```

### Arrêter et supprimer les volumes
```bash
docker-compose down -v
```

### Supprimer les images Docker (optionnel)
```bash
docker rmi apache/spark:3.5.0
```

## Dépannage

### Le worker ne se connecte pas au master

Attendez quelques secondes après le démarrage et vérifiez les logs :
```bash
docker logs spark-worker-1
```

### Erreur "Path not found"

Vérifiez que le fichier de données existe dans `datas/` et que le nom correspond à celui dans `event_counter.py`.

### Erreur de mémoire

Augmentez la mémoire du worker dans `docker-compose.yml` :
```yaml
environment:
  - SPARK_WORKER_MEMORY=4G
```

## Technologies utilisées

- **Apache Spark 3.5.0** - Framework de traitement distribué
- **PySpark** - API Python pour Spark
- **Docker** - Conteneurisation
- **Docker Compose** - Orchestration des conteneurs
- **GDELT 2.0** - Base de données d'événements mondiaux

## Références

- [Apache Spark Documentation](https://spark.apache.org/docs/latest/)
- [GDELT Project](https://www.gdeltproject.org/)
- [GDELT 2.0 Event Database](https://blog.gdeltproject.org/gdelt-2-0-our-global-world-in-realtime/)
- [Docker Hub - Apache Spark](https://hub.docker.com/r/apache/spark)
