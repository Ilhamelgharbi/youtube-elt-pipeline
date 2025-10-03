# 📋 YouTube ELT Pipeline - Guide Étape par Étape

## 🎯 Objectif du Projet
Créer un pipeline ELT automatisé pour extraire, charger et transformer les données YouTube avec Apache Airflow, PostgreSQL et Soda Core.

---

## 📅 Timeline du Projet (10 jours)
- **Jours 1-2**: Setup et DAG d'extraction (produce_JSON)
- **Jours 3-4**: PostgreSQL et DAG de chargement (update_db)
- **Jours 5-6**: Data Quality avec Soda Core
- **Jours 7-8**: Tests et CI/CD
- **Jours 9-10**: Documentation et finalisation

---

## 🚀 Phase 1: Initialisation du Projet (Jour 1)

### ✅ Étape 1.1: Installer Astro CLI
```powershell
# Vérifier si Astro CLI est installé
astro version

# Si non installé, installer avec:
winget install -e --id Astronomer.Astro
```

### ✅ Étape 1.2: Initialiser le Projet Astro
```powershell
# Créer le dossier du projet
cd C:\Users\user\Desktop\version-final

# Initialiser Astro (déjà fait ✅)
astro dev init

# Structure créée:
# ├── dags/              # Vos DAGs Airflow
# ├── include/           # Données et scripts
# ├── plugins/           # Plugins Airflow personnalisés
# ├── tests/             # Tests unitaires
# ├── Dockerfile         # Configuration Docker
# ├── requirements.txt   # Dépendances Python
# ├── .env              # Variables d'environnement
# └── packages.txt       # Packages système
```

### ✅ Étape 1.3: Configurer les Dépendances
```powershell
# Éditer requirements.txt (déjà fait ✅)
```

**Contenu de requirements.txt:**
```txt
# YouTube API
google-api-python-client==2.108.0
google-auth==2.23.4
isodate==0.6.1

# PostgreSQL
psycopg2-binary==2.9.7
apache-airflow-providers-postgres==5.7.1

# Data Quality
soda-core-postgres==3.1.6

# Data Processing
pandas==2.1.3
numpy==1.24.4

# Testing
pytest==7.4.3
```

### ✅ Étape 1.4: Configurer les Variables d'Environnement
```powershell
# Éditer .env (déjà fait ✅)
```

**Contenu de .env:**
```env
# YouTube API
YOUTUBE_API_KEY=AIzaSyDyhE7sl0qtEhsZX0e8WXSdYNR6bEikHXQ
YOUTUBE_CHANNEL_ID=UCX6OQ3DkcsbYNE6H8uQQuVA
YOUTUBE_CHANNEL_HANDLE=MrBeast
YOUTUBE_MAX_RESULTS=50

# PostgreSQL Data Warehouse
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=youtube_dwh
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
```

---

## 📊 Phase 2: DAG d'Extraction - produce_JSON (Jours 1-2)

### ✅ Étape 2.1: Créer le DAG d'Extraction
**Fichier: `dags/youtube_extract.py`** (déjà créé ✅)

Ce DAG fait:
1. Se connecte à l'API YouTube v3
2. Récupère les vidéos de la chaîne MrBeast
3. Extrait les métadonnées (titre, vues, likes, durée, etc.)
4. Sauvegarde dans un fichier JSON horodaté
5. Stocke le chemin dans XCom pour les DAGs suivants

### ✅ Étape 2.2: Créer les Utilitaires YouTube
**Fichier: `dags/utils/youtube_utils.py`** (déjà créé ✅)

Contient:
- `YouTubeAPIClient`: Classe pour gérer l'API YouTube
- `iso_duration_to_readable()`: Convertir durée ISO 8601
- `clean_video_data()`: Nettoyer les données brutes
- `validate_video_data()`: Valider les données

### ✅ Étape 2.3: Démarrer Airflow Localement
```powershell
# Démarrer Airflow avec Astro
astro dev start

# Attendre que tous les conteneurs démarrent
# Airflow UI: http://localhost:8080
# Username: admin
# Password: admin
```

### ✅ Étape 2.4: Tester le DAG d'Extraction
```powershell
# 1. Aller sur http://localhost:8080
# 2. Trouver le DAG "produce_JSON"
# 3. Activer le DAG (toggle ON)
# 4. Cliquer sur "Trigger DAG" (▶️)
# 5. Vérifier les logs

# Ou via CLI:
astro dev bash
airflow dags test produce_JSON 2025-10-02
exit
```

### ✅ Étape 2.5: Vérifier les Fichiers JSON Créés
```powershell
# Vérifier dans le dossier include/youtube_data
ls include/youtube_data/

# Lire un fichier JSON
cat include/youtube_data/MrBeast_20251002_143000.json
```

**Format JSON attendu:**
```json
{
    "channel_handle": "MrBeast",
    "channel_id": "UCX6OQ3DkcsbYNE6H8uQQuVA",
    "extraction_date": "2025-10-02T14:30:00.123456",
    "total_videos": 50,
    "videos": [
        {
            "video_id": "4l97aNza_Zc",
            "title": "Survive 30 Days Chained To Your Ex",
            "published_at": "2025-09-13T16:00:01Z",
            "duration_iso": "PT37M4S",
            "duration_readable": "37:04",
            "duration_seconds": 2224,
            "view_count": 54506132,
            "like_count": 1833636,
            "comment_count": 27466,
            "thumbnail_url": "https://..."
        }
    ]
}
```

---

## 🗄️ Phase 3: PostgreSQL Data Warehouse (Jours 3-4)

### ✅ Étape 3.1: Créer les Scripts SQL
**Fichier: `include/sql/create_schemas.sql`**

```sql
-- Créer les schémas
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS core;

-- Schéma STAGING: Données brutes
CREATE TABLE IF NOT EXISTS staging.youtube_videos_raw (
    id SERIAL PRIMARY KEY,
    video_id VARCHAR(50),
    title TEXT,
    description TEXT,
    published_at TIMESTAMP,
    duration_iso VARCHAR(50),
    duration_seconds INTEGER,
    view_count BIGINT,
    like_count BIGINT,
    comment_count BIGINT,
    channel_id VARCHAR(50),
    channel_handle VARCHAR(100),
    extraction_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Schéma CORE: Données transformées
CREATE TABLE IF NOT EXISTS core.videos (
    video_id VARCHAR(50) PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    published_at TIMESTAMP NOT NULL,
    duration_seconds INTEGER,
    duration_readable VARCHAR(20),
    channel_id VARCHAR(50) NOT NULL,
    channel_handle VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS core.video_statistics (
    id SERIAL PRIMARY KEY,
    video_id VARCHAR(50) REFERENCES core.videos(video_id),
    view_count BIGINT DEFAULT 0,
    like_count BIGINT DEFAULT 0,
    comment_count BIGINT DEFAULT 0,
    recorded_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour performance
CREATE INDEX IF NOT EXISTS idx_videos_channel ON core.videos(channel_id);
CREATE INDEX IF NOT EXISTS idx_stats_video ON core.video_statistics(video_id);
CREATE INDEX IF NOT EXISTS idx_stats_recorded ON core.video_statistics(recorded_at);
```

### ✅ Étape 3.2: Créer le DAG update_db
**Fichier: `dags/youtube_load_db.py`**

Ce DAG fait:
1. Lit le dernier fichier JSON créé
2. Charge les données dans `staging.youtube_videos_raw`
3. Transforme et nettoie les données
4. Insère dans `core.videos` et `core.video_statistics`
5. Gère les doublons et l'historique

### ✅ Étape 3.3: Configurer la Connexion PostgreSQL
```powershell
# Via l'interface Airflow:
# 1. Aller sur http://localhost:8080
# 2. Admin → Connections
# 3. Ajouter une nouvelle connexion:
#    - Conn Id: postgres_dwh
#    - Conn Type: Postgres
#    - Host: postgres
#    - Schema: youtube_dwh
#    - Login: postgres
#    - Password: postgres
#    - Port: 5432

# Ou via CLI:
astro dev bash
airflow connections add postgres_dwh \
    --conn-type postgres \
    --conn-host postgres \
    --conn-schema youtube_dwh \
    --conn-login postgres \
    --conn-password postgres \
    --conn-port 5432
exit
```

### ✅ Étape 3.4: Tester le DAG update_db
```powershell
# Trigger le DAG
# 1. S'assurer que produce_JSON a été exécuté
# 2. Activer update_db
# 3. Trigger le DAG
# 4. Vérifier les logs
```

### ✅ Étape 3.5: Vérifier les Données dans PostgreSQL
```powershell
# Se connecter à PostgreSQL
astro dev bash
psql -h postgres -U postgres -d youtube_dwh

# Vérifier les données
SELECT COUNT(*) FROM staging.youtube_videos_raw;
SELECT COUNT(*) FROM core.videos;
SELECT COUNT(*) FROM core.video_statistics;

# Voir les dernières vidéos
SELECT video_id, title, view_count, published_at 
FROM core.videos 
ORDER BY published_at DESC 
LIMIT 5;

\q
exit
```

---

## ✅ Phase 4: Data Quality avec Soda Core (Jours 5-6)

### ✅ Étape 4.1: Créer la Configuration Soda
**Fichier: `include/soda/configuration.yml`**

```yaml
data_source postgres_dwh:
  type: postgres
  host: ${POSTGRES_HOST}
  port: ${POSTGRES_PORT}
  username: ${POSTGRES_USER}
  password: ${POSTGRES_PASSWORD}
  database: ${POSTGRES_DB}
  schema: core
```

### ✅ Étape 4.2: Créer les Checks de Qualité
**Fichier: `include/soda/checks/videos_quality.yml`**

```yaml
checks for videos:
  # Complétude
  - row_count > 0
  - missing_count(video_id) = 0
  - missing_count(title) = 0
  - missing_count(published_at) = 0
  
  # Validité
  - invalid_count(video_id) = 0:
      valid length: 11
  - invalid_count(view_count) = 0:
      valid min: 0
  - invalid_count(duration_seconds) = 0:
      valid min: 0
  
  # Unicité
  - duplicate_count(video_id) = 0
  
  # Fraîcheur
  - freshness(published_at) < 1d

checks for video_statistics:
  - row_count > 0
  - missing_count(video_id) = 0
  - invalid_count(view_count) = 0:
      valid min: 0
```

### ✅ Étape 4.3: Créer le DAG data_quality
**Fichier: `dags/youtube_data_quality.py`**

Ce DAG:
1. Exécute les checks Soda Core
2. Valide la qualité des données
3. Envoie des alertes si problèmes
4. Génère un rapport de qualité

### ✅ Étape 4.4: Tester les Checks de Qualité
```powershell
# Trigger le DAG data_quality
# Vérifier les logs pour voir les résultats
```

---

## 🔗 Phase 5: Orchestration des DAGs (Jour 6) ✅ COMPLETE

### ✅ Étape 5.1: Orchestration via TriggerDagRunOperator (DONE!)

**Votre implémentation actuelle (déjà en place):**

```
produce_JSON (manuel)
     ↓
update_db (manuel)
  ├─ find_json_task
  ├─ load_staging_task
  ├─ transform_core_task
  ├─ verify_task
  └─ trigger_quality_check ──→ Automatically triggers data_quality!
```

**Fichier: `dags/youtube_load_db.py` - Lines 372-378**
```python
# Task 5: Trigger data quality validation
trigger_quality_check = TriggerDagRunOperator(
    task_id="trigger_data_quality",
    trigger_dag_id="data_quality",  # ✅ Auto-triggers quality checks!
    wait_for_completion=False,
)

# Dependency chain
find_json_task >> load_staging_task >> transform_core_task >> verify_task >> trigger_quality_check
```

### ✅ Étape 5.2: Comment Utiliser l'Orchestration

**Option 1: Pipeline Complet (Recommandé)**
```powershell
# 1. Extraire les données YouTube
# Airflow UI → produce_JSON → Trigger DAG

# 2. Charger dans PostgreSQL (déclenche automatiquement data_quality!)
# Airflow UI → update_db → Trigger DAG
#   ↳ Cela exécute automatiquement data_quality à la fin!
```

**Option 2: Via CLI**
```powershell
astro dev bash

# Extraire
airflow dags test produce_JSON 2025-10-02

# Charger (trigger data_quality automatiquement)
airflow dags test update_db 2025-10-02

exit
```

### 💡 Pourquoi Cette Approche?

**Avantages:**
- ✅ **Flexibilité**: Exécuter `produce_JSON` quotidiennement, `update_db` à la demande
- ✅ **Debugging**: Chaque DAG a ses propres logs indépendants
- ✅ **Best Practice**: Airflow recommande le découplage des DAGs
- ✅ **Réutilisabilité**: Chaque DAG peut être testé/exécuté séparément

**Alternative (Non implémentée - pas nécessaire):**
Si vous voulez un DAG master qui orchestre tout en une seule fois, vous pourriez créer `youtube_pipeline_main.py`, mais ce n'est **pas requis** car vous avez déjà l'orchestration via `TriggerDagRunOperator`

---

## 🧪 Phase 6: Tests (Jours 7-8)

### ✅ Étape 6.1: Créer les Tests Unitaires
**Fichier: `tests/dags/test_youtube_extract.py`**

Tests à créer:
- Test de la connexion API YouTube
- Test de la conversion de durée
- Test de la validation des données
- Test de la création de fichier JSON

### ✅ Étape 6.2: Créer les Tests d'Intégration
**Fichier: `tests/integration/test_pipeline.py`**

Tests à créer:
- Test du pipeline complet
- Test de la connexion PostgreSQL
- Test des transformations

### ✅ Étape 6.3: Exécuter les Tests
```powershell
# Exécuter tous les tests
astro dev pytest

# Ou spécifiquement:
astro dev bash
pytest tests/ -v
exit
```

---

## 🚀 Phase 7: CI/CD avec GitHub Actions (Jour 8)

### ✅ Étape 7.1: Créer le Workflow GitHub
**Fichier: `.github/workflows/ci-cd.yml`**

Pipeline CI/CD:
1. Lint du code (Black, Flake8)
2. Tests unitaires
3. Tests d'intégration
4. Build Docker
5. Déploiement (optionnel)

### ✅ Étape 7.2: Configurer les Secrets GitHub
```
DOCKER_USERNAME
DOCKER_PASSWORD
ASTRO_API_KEY (si déploiement Astronomer)
```

---

## 📊 Phase 8: Dashboard (Bonus - Jour 9)

### ✅ Étape 8.1: Créer le Dashboard Streamlit
**Fichier: `dashboard/app.py`**

Dashboard affichant:
- Nombre total de vidéos
- Vues totales
- Vidéos les plus populaires
- Évolution des statistiques
- Graphiques interactifs

### ✅ Étape 8.2: Lancer le Dashboard
```powershell
streamlit run dashboard/app.py
```

---

## 📝 Phase 9: Documentation (Jour 10)

### ✅ Étape 9.1: Créer le README Complet
**Fichier: `README.md`**

Sections:
- Description du projet
- Architecture
- Installation
- Configuration
- Utilisation
- Tests
- Déploiement
- Screenshots

### ✅ Étape 9.2: Ajouter la Documentation des DAGs
Documenter chaque DAG avec:
- Description
- Paramètres
- Dépendances
- Schedule
- Exemples

---

## 🎯 Checklist Finale

### ✅ Fonctionnalités
- [ ] DAG produce_JSON fonctionne
- [ ] DAG update_db charge les données
- [ ] DAG data_quality valide les données
- [ ] Pipeline orchestré fonctionne bout en bout
- [ ] Gestion des erreurs et retry
- [ ] Logs détaillés

### ✅ Architecture
- [ ] Structure modulaire
- [ ] Code bien organisé
- [ ] Configuration centralisée
- [ ] Secrets sécurisés

### ✅ PostgreSQL
- [ ] Schémas staging et core créés
- [ ] Tables avec index
- [ ] Transformations implémentées
- [ ] Accès depuis Airflow et outils externes

### ✅ Tests
- [ ] 20+ tests unitaires
- [ ] Tests d'intégration
- [ ] Tests de qualité des données
- [ ] Tous les tests passent

### ✅ Documentation
- [ ] README complet
- [ ] Docstrings sur toutes les fonctions
- [ ] Commentaires dans le code
- [ ] Guide d'installation

### ✅ Déploiement
- [ ] Docker fonctionne
- [ ] CI/CD configuré
- [ ] Screenshots capturés
- [ ] Prêt pour démonstration

---

## 🔧 Commandes Utiles

### Astro CLI
```powershell
# Démarrer Airflow
astro dev start

# Arrêter Airflow
astro dev stop

# Redémarrer Airflow
astro dev restart

# Voir les logs
astro dev logs

# Bash dans le conteneur
astro dev bash

# Exécuter les tests
astro dev pytest

# Valider les DAGs
astro dev parse
```

### Airflow CLI (dans le conteneur)
```bash
# Lister les DAGs
airflow dags list

# Tester un DAG
airflow dags test produce_JSON 2025-10-02

# Lister les tâches
airflow tasks list produce_JSON

# Voir les variables
airflow variables list

# Voir les connexions
airflow connections list
```

### PostgreSQL
```bash
# Se connecter
psql -h postgres -U postgres -d youtube_dwh

# Commandes utiles
\dt staging.*     # Lister tables staging
\dt core.*        # Lister tables core
\d+ core.videos   # Décrire une table
\q                # Quitter
```

---

## 📚 Ressources

### Documentation
- [Astro CLI](https://docs.astronomer.io/astro/cli/overview)
- [Apache Airflow](https://airflow.apache.org/docs/)
- [YouTube API v3](https://developers.google.com/youtube/v3)
- [Soda Core](https://docs.soda.io/soda-core/)
- [PostgreSQL](https://www.postgresql.org/docs/)

### Tutoriels
- [Airflow Best Practices](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html)
- [ELT vs ETL](https://www.astronomer.io/blog/etl-vs-elt/)

---

## 🎓 Conseils

1. **Tester fréquemment**: Après chaque étape, tester le code
2. **Commiter souvent**: Faire des commits réguliers avec messages clairs
3. **Documenter en avançant**: Ne pas attendre la fin pour documenter
4. **Gérer les erreurs**: Prévoir les cas d'erreur dès le début
5. **Respecter les quotas API**: Ne pas dépasser 10000 unités/jour
6. **Versionner les données**: Garder l'historique des extractions

---

## ⏱️ Estimation du Temps par Phase

| Phase | Durée | Tâches |
|-------|-------|--------|
| Setup | 2h | Astro init, configuration |
| DAG Extract | 4h | Création, tests |
| PostgreSQL | 6h | Schémas, DAG load, tests |
| Data Quality | 4h | Soda checks, DAG quality |
| Orchestration | 2h | DAG principal |
| Tests | 8h | 20+ tests unitaires/intégration |
| CI/CD | 4h | GitHub Actions |
| Dashboard | 4h | Streamlit (bonus) |
| Documentation | 4h | README, captures |
| **TOTAL** | **38h** | Sur 10 jours = 4h/jour |

---

## 📧 Support

Si vous rencontrez des problèmes:
1. Vérifier les logs Airflow
2. Vérifier les connexions PostgreSQL
3. Vérifier les quotas API YouTube
4. Consulter la documentation

---

**Bon courage pour votre projet! 🚀**
