# Atelier 1 : Cluster Spark avec Docker - Analyse GDELT

Mise en place d'un cluster Apache Spark local avec Docker pour analyser les événements GDELT et compter les événements par pays.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Docker Network (spark-net)                    │
│                                                                      │
│  ┌─────────────────┐                                                │
│  │  Spark Master   │                                                │
│  │                 │                                                │
│  │  Port: 7077     │                                                │
│  │  UI: 8080       │                                                │
│  │  App UI: 4040   │                                                │
│  └────────┬────────┘                                                │
│           │                                                          │
│     ┌─────┴─────┐                                                   │
│     │           │                                                   │
│  ┌──▼───────┐ ┌─▼────────┐                                         │
│  │ Worker 1 │ │ Worker 2 │                                         │
│  │ Memory:2G│ │ Memory:2G│                                         │
│  │ Cores: 2 │ │ Cores: 2 │                                         │
│  │ UI: 8081 │ │ UI: 8082 │                                         │
│  └──────────┘ └──────────┘                                         │
│           │           │                                             │
│           └─────┬─────┘                                             │
│          ┌──────▼──────┐                                            │
│          │   Volumes   │                                            │
│          │  - /data    │                                            │
│          │  - /app     │                                            │
│          │  - /output  │                                            │
│          └─────────────┘                                            │
└─────────────────────────────────────────────────────────────────────┘
```

## Prérequis

- Docker Desktop installé et en cours d'exécution
- Docker Compose (inclus avec Docker Desktop)
- Minimum 4 Go de RAM disponible

## Structure du projet

```
Atelier 1/
├── docker-compose.yml      # Configuration du cluster Spark (1 master + 2 workers)
├── event_counter.py        # Programme PySpark orienté objet avec CLI
├── timer.py                # Module de mesure du temps d'exécution
├── README.md               # Documentation (ce fichier)
├── datas/
│   ├── 20251208.export.CSV       # Données GDELT (111,373 événements)
│   └── GDELT.MASTERREDUCEDV2.TXT # Données GDELT 1979-2013
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
- Démarre les 2 Spark Workers
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
spark-worker-2  Up X minutes    0.0.0.0:8082->8081
```

## Utilisation

### Exécuter le job PySpark via Docker (Recommandé)

#### Sur Windows (Git Bash ou PowerShell) :
```bash
docker exec spark-master //opt/spark/bin/spark-submit --master spark://spark-master:7077 //app/event_counter.py
```

#### Sur Linux/Mac :
```bash
docker exec spark-master /opt/spark/bin/spark-submit --master spark://spark-master:7077 /app/event_counter.py
```

#### Avec des arguments personnalisés :
```bash
docker exec spark-master //opt/spark/bin/spark-submit \
  --master spark://spark-master:7077 \
  //app/event_counter.py \
  --input /data/20251208.export.CSV \
  --output /output/event_counts_by_country
```

### Sortie attendue

```
Configuration:
  - Master: local[*]
  - Input:  datas/20251208.export.CSV
  - Output: output/event_counts_by_country
============================================================
GDELT Event Counter - Comptage des événements par pays
============================================================

Lecture des données depuis: datas/20251208.export.CSV
Nombre total d'événements chargés: 111373
[TIMER] load_data: 2.35 secondes

[TIMER] count_by_country: 0.12 secondes

============================================================
TOP 30 des pays par nombre d'événements:
============================================================
+-----------+----------+
|CountryCode|EventCount|
+-----------+----------+
|US         |30787     |
|UK         |6115      |
|IN         |6025      |
...

Sauvegarde des résultats vers: output/event_counts_by_country
Sauvegarde terminée avec succès!
[TIMER] save_results: 1.45 secondes
[TIMER] run: 5.92 secondes
```

## Résultats

Les résultats sont sauvegardés dans le dossier `output/event_counts_by_country/` au format CSV :

```csv
CountryCode,EventCount
US,30787
UK,6115
IN,6025
IS,4008
NI,3682
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
| Spark Worker 1 UI | http://localhost:8081 | Détails du worker 1, exécutions |
| Spark Worker 2 UI | http://localhost:8082 | Détails du worker 2, exécutions |
| Spark Application UI | http://localhost:4040 | Jobs en cours, stages, DAG |

> Note : L'interface Application UI (4040) n'est disponible que pendant l'exécution d'un job.

## Programme PySpark (event_counter.py)

### Architecture orientée objet

Le programme utilise une classe `GDELTEventCounter` qui encapsule toute la logique de traitement :

```python
class GDELTEventCounter:
    """Classe pour compter les événements GDELT par pays."""

    def __init__(self, master: str, app_name: str)  # Initialise la session Spark
    def load_data(self, input_path: str)            # Charge les données GDELT
    def count_by_country(self)                      # Compte les événements par pays
    def show_results(self, n: int = 30)             # Affiche les résultats
    def save_results(self, output_path: str)        # Sauvegarde en CSV
    def run(self, input_path: str, output_path: str)# Pipeline complet
    def stop(self)                                  # Arrête la session Spark
```

### Arguments de ligne de commande

| Argument | Description | Valeur par défaut |
|----------|-------------|-------------------|
| `--input` | Chemin du fichier GDELT à analyser | `datas/20251208.export.CSV` |
| `--output` | Chemin du dossier de sortie CSV | `output/event_counts_by_country` |
| `--master` | URL du Spark Master | `local[*]` |

### Exemples d'utilisation

```bash
# Utilisation par défaut (mode local)
python event_counter.py

# Avec un fichier d'entrée différent
python event_counter.py --input datas/autre_fichier.CSV

# Connexion au cluster Docker
python event_counter.py --master spark://localhost:7077

# Configuration complète
python event_counter.py \
  --master spark://localhost:7077 \
  --input datas/20251208.export.CSV \
  --output output/resultats
```

## Exécution locale (sans Docker)

### Prérequis

1. **Java 8, 11 ou 17** installé
2. **Apache Spark 3.5.x** installé
3. Variables d'environnement configurées :
   ```bash
   SPARK_HOME=C:\spark-3.5.7-bin-hadoop3  # Chemin vers Spark
   PATH=%PATH%;%SPARK_HOME%\bin
   ```

### Sur Windows : Configuration Hadoop

Pour que Spark puisse écrire des fichiers CSV sur Windows, il faut configurer Hadoop :

1. **Créer le dossier Hadoop** :
   ```powershell
   mkdir C:\hadoop\bin
   ```

2. **Télécharger les binaires Hadoop** depuis :
   - https://github.com/cdarlint/winutils/tree/master/hadoop-3.3.5/bin
   - Télécharger tous les fichiers du dossier `bin` (notamment `winutils.exe`, `hadoop.dll`, etc.)

3. **Placer les fichiers** dans `C:\hadoop\bin\`

4. **Copier hadoop.dll dans System32** (nécessite les droits administrateur) :
   ```powershell
   Copy-Item "C:\hadoop\bin\hadoop.dll" -Destination "C:\Windows\System32\" -Force
   ```

5. **Configurer la variable d'environnement** :
   ```powershell
   setx HADOOP_HOME "C:\hadoop"
   ```

6. **Redémarrer le terminal** et exécuter :
   ```bash
   spark-submit event_counter.py
   ```

> **Note** : L'exécution via Docker est recommandée car elle ne nécessite aucune configuration Hadoop supplémentaire.

## Mesure des performances

Le module `timer.py` permet de mesurer et comparer les temps d'exécution entre l'exécution locale et le cluster Docker.

### Comparer Local vs Cluster

**Exécution locale (Windows) :**
```bash
spark-submit event_counter.py --input datas/GDELT.MASTERREDUCEDV2.TXT
```

**Exécution sur le cluster Docker (2 workers) :**
```bash
docker exec spark-master //opt/spark/bin/spark-submit \
  --master spark://spark-master:7077 \
  //app/event_counter.py \
  --input /data/GDELT.MASTERREDUCEDV2.TXT
```

### Module timer.py

Le décorateur `@timed` mesure automatiquement le temps de chaque méthode :

```python
from timer import timed

@timed
def ma_fonction():
    # Le temps d'exécution sera affiché automatiquement
    pass
```

Sortie : `[TIMER] ma_fonction: X.XX secondes`

## Données GDELT

### Format des fichiers

- **Format** : CSV avec séparateur tabulation (`\t`)
- **En-tête** : Non (les fichiers GDELT n'ont pas d'en-tête)
- **Encodage** : UTF-8

### Colonne utilisée

Le programme utilise la **colonne 52** (index 51) qui correspond au champ `ActionGeo_CountryCode` dans le schéma GDELT 2.0 Events. Ce champ contient le code pays FIPS à 2 lettres (ex: US, UK, FR, IN).

### Schéma GDELT 2.0 (colonnes principales)

| Index | Nom | Description |
|-------|-----|-------------|
| 0 | GlobalEventID | Identifiant unique de l'événement |
| 1 | Day | Date au format YYYYMMDD |
| 5 | Actor1Code | Code de l'acteur 1 |
| 15 | Actor2Code | Code de l'acteur 2 |
| 50 | ActionGeo_FullName | Localisation complète de l'action |
| 51 | ActionGeo_CountryCode | Code pays FIPS (2 lettres) |
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
docker logs spark-worker-2
```

### Erreur "Path not found"

Vérifiez que le fichier de données existe dans `datas/` et que le nom correspond à celui passé en argument (par défaut `datas/20251208.export.CSV`).

### Erreur de mémoire

Augmentez la mémoire des workers dans `docker-compose.yml` :
```yaml
environment:
  - SPARK_WORKER_MEMORY=4G
```

### Erreur HADOOP_HOME sur Windows (exécution locale)

Si vous voyez l'erreur `HADOOP_HOME and hadoop.home.dir are unset`, suivez les instructions de la section "Exécution locale - Configuration Hadoop".

### Erreur NativeIO / hadoop.dll sur Windows

Si vous voyez `UnsatisfiedLinkError: org.apache.hadoop.io.nativeio.NativeIO` :
1. Téléchargez `hadoop.dll` depuis le dépôt winutils
2. Copiez-le dans `C:\hadoop\bin\` ET dans `C:\Windows\System32\`
3. Redémarrez votre terminal

> **Solution recommandée** : Utilisez Docker pour éviter ces problèmes de compatibilité Windows.

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
