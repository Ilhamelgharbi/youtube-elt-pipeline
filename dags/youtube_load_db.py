"""
🎯 YouTube ELT Pipeline - DAG: update_db
==========================================
DAG de chargement et transformation des données YouTube en PostgreSQL

Fonctionnalités:
1️⃣ Synchronisation JSON → Staging (UPSERT + DELETE)
2️⃣ Transformation Staging → Core (avec analyse de durée)
3️⃣ Déclenchement des contrôles qualité

Architecture:
- Schéma staging: Données brutes YouTube
- Schéma core: Données transformées et enrichies
- Gestion automatique des doublons et de l'historique

Orchestration:
produce_JSON → update_db → data_quality
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime, timedelta
import json
import logging
from pathlib import Path

# ==========================================
# 🔧 CONFIGURATION
# ==========================================
DATA_PATH = "/usr/local/airflow/include/youtube_data"
POSTGRES_CONN_ID = "postgres_dwh"


def find_latest_json(**context):
    """
    🔍 Recherche du fichier JSON le plus récent
    
    Returns:
        str: Chemin absolu du fichier JSON le plus récent
    
    Raises:
        FileNotFoundError: Si aucun fichier JSON n'est trouvé
    """
    json_files = list(Path(DATA_PATH).glob("*.json"))
    if not json_files:
        raise FileNotFoundError(f"❌ Aucun fichier JSON trouvé dans {DATA_PATH}")
    
    latest = max(json_files, key=lambda f: f.stat().st_mtime)
    logging.info(f"✅ Fichier JSON sélectionné: {latest.name}")
    
    context['ti'].xcom_push(key='json_file', value=str(latest))
    return str(latest)


def sync_to_staging(**context):
    """
    📥 Synchronisation JSON → Schéma Staging
    
    Opérations:
    - UPSERT: Insertion de nouvelles vidéos, mise à jour des existantes
    - DELETE: Suppression des vidéos absentes du JSON
    - Dédoublonnage: Garantie d'unicité des video_ids
    
    Returns:
        int: Nombre de vidéos synchronisées
    """
    # Récupération du fichier JSON
    json_file = context['ti'].xcom_pull(task_ids='find_latest_json', key='json_file')
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    videos = data['videos']
    channel_id = data['channel_id']
    channel_handle = data['channel_handle']
    extraction_date = data['extraction_date']
    
    # Dédoublonnage dans le JSON
    unique_videos = {v['video_id']: v for v in videos}
    videos = list(unique_videos.values())
    
    logging.info(f"📊 {len(videos)} vidéos uniques extraites du JSON")
    
    # Connexion à PostgreSQL
    pg_hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
    
    # Récupération des IDs existants en staging
    existing_ids = set()
    try:
        result = pg_hook.get_records("SELECT video_id FROM staging.youtube_videos_raw")
        existing_ids = {row[0] for row in result}
        logging.info(f"📂 {len(existing_ids)} vidéos déjà en staging")
    except Exception as e:
        logging.warning(f"⚠️ Impossible de récupérer les IDs existants: {e}")
    
    json_video_ids = {v['video_id'] for v in videos}
    
    # ==========================================
    # UPSERT: Insertion et mise à jour
    # ==========================================
    upsert_query = """
        INSERT INTO staging.youtube_videos_raw (
            video_id, title, published_at, duration, duration_readable,
            view_count, like_count, comment_count,
            channel_id, channel_handle, extraction_date
        ) VALUES (
            %(video_id)s, %(title)s, %(published_at)s, %(duration)s, %(duration_readable)s,
            %(view_count)s, %(like_count)s, %(comment_count)s,
            %(channel_id)s, %(channel_handle)s, %(extraction_date)s
        )
        ON CONFLICT (video_id) DO UPDATE SET
            title = EXCLUDED.title,
            view_count = EXCLUDED.view_count,
            like_count = EXCLUDED.like_count,
            comment_count = EXCLUDED.comment_count,
            extraction_date = EXCLUDED.extraction_date
    """
    
    inserted = updated = 0
    for video in videos:
        # Gestion des valeurs None pour les statistiques
        view_count = video.get('view_count')
        like_count = video.get('like_count')
        comment_count = video.get('comment_count')
        
        pg_hook.run(upsert_query, parameters={
            'video_id': video['video_id'],
            'title': video['title'],
            'published_at': video['published_at'],
            'duration': video['duration'],
            'duration_readable': video['duration_readable'],
            'view_count': int(view_count) if view_count is not None else 0,
            'like_count': int(like_count) if like_count is not None else 0,
            'comment_count': int(comment_count) if comment_count is not None else 0,
            'channel_id': channel_id,
            'channel_handle': channel_handle,
            'extraction_date': extraction_date,
        })
        if video['video_id'] in existing_ids:
            updated += 1
        else:
            inserted += 1
    
    logging.info(f"✅ Insertions: {inserted} | Mises à jour: {updated}")
    
    # ==========================================
    # DELETE: Suppression des vidéos obsolètes
    # ==========================================
    to_delete = existing_ids - json_video_ids
    if to_delete:
        pg_hook.run(
            "DELETE FROM staging.youtube_videos_raw WHERE video_id = ANY(%(ids)s)",
            parameters={'ids': list(to_delete)}
        )
        logging.info(f"🗑️ Supprimées: {len(to_delete)} vidéos obsolètes")
    
    # Passer les données à la tâche suivante
    context['ti'].xcom_push(key='extraction_date', value=extraction_date)
    return len(videos)


def transform_to_core(**context):
    """
    🔄 Transformation Staging → Core Tables
    
    Transformations appliquées:
    - Conversion ISO 8601 (PT22M26S) → PostgreSQL INTERVAL
    - Labellisation: 'short' (<1 min) ou 'long' (≥1 min)
    - Gestion de l'historique: created_at, updated_at
    
    Tables cibles:
    - core.videos: Métadonnées enrichies des vidéos
    - core.video_statistics: Historique des statistiques
    
    Returns:
        int: Nombre de vidéos transformées
    """
    extraction_date = context['ti'].xcom_pull(task_ids='sync_to_staging', key='extraction_date')
    pg_hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
    
    logging.info("🔄 Début de la transformation staging → core...")
    
    # ==========================================
    # UPSERT dans core.videos avec transformations
    # ==========================================
    pg_hook.run("""
        WITH duration_calc AS (
            SELECT 
                video_id,
                title,
                published_at,
                duration,
                duration_readable,
                channel_id,
                channel_handle,
                -- Conversion ISO 8601 (PT22M26S) → INTERVAL PostgreSQL
                duration::INTERVAL AS duration_seconds,
                -- Calcul des secondes totales pour labellisation
                EXTRACT(EPOCH FROM duration::interval) AS total_seconds
            FROM staging.youtube_videos_raw
        )
        INSERT INTO core.videos (
            video_id, title, published_at, duration, duration_readable,
            duration_seconds, duration_label,
            channel_id, channel_handle, created_at, updated_at
        )
        SELECT DISTINCT 
            video_id,
            title,
            published_at,
            duration,
            duration_readable,
            duration_seconds,
            CASE 
                WHEN total_seconds < 60 THEN 'short'
                ELSE 'long'
            END AS duration_label,
            channel_id,
            channel_handle,
            NOW(),
            NOW()
        FROM duration_calc
        ON CONFLICT (video_id) DO UPDATE SET
            title = EXCLUDED.title,
            duration_seconds = EXCLUDED.duration_seconds,
            duration_label = EXCLUDED.duration_label,
            updated_at = NOW()
    """)
    
    logging.info("✅ Table core.videos mise à jour")
    
    # ==========================================
    # DELETE: Suppression des vidéos absentes de staging
    # ==========================================
    # First, count how many will be deleted
    to_delete_core = pg_hook.get_first("""
        SELECT COUNT(*) FROM core.videos
        WHERE video_id NOT IN (
            SELECT video_id FROM staging.youtube_videos_raw
        )
    """)[0]
    
    # Then delete them
    if to_delete_core > 0:
        pg_hook.run("""
            DELETE FROM core.videos
            WHERE video_id NOT IN (
                SELECT video_id FROM staging.youtube_videos_raw
            )
        """)
        logging.info(f"🗑️ Supprimées de core.videos: {to_delete_core} vidéos absentes de staging")
    else:
        logging.info("✅ Aucune vidéo à supprimer de core.videos")
    
    # ==========================================
    # INSERT dans core.video_statistics (historique)
    # ==========================================
    pg_hook.run("""
        INSERT INTO core.video_statistics (
            video_id, view_count, like_count, comment_count, recorded_at
        )
        SELECT video_id, view_count, like_count, comment_count, %(date)s::timestamp
        FROM staging.youtube_videos_raw
    """, parameters={'date': extraction_date})
    
    logging.info("✅ Table core.video_statistics mise à jour")
    
    # Comptage final
    count = pg_hook.get_first("SELECT COUNT(*) FROM core.videos")[0]
    logging.info(f"✅ Transformation terminée: {count} vidéos dans core.videos")
    return count


# ==========================================
# 🎯 CONFIGURATION DU DAG
# ==========================================

default_args = {
    "owner": "airflow",
    "start_date": datetime(2025, 9, 1),
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="update_db",
    description="📥 Load YouTube JSON → PostgreSQL (staging → core avec transformations)",
    default_args=default_args,
    schedule=None,  # Déclenché automatiquement par produce_JSON
    catchup=False,
    tags=["youtube", "etl", "postgresql"],
) as dag:
    
    # ==========================================
    # 📋 DÉFINITION DES TÂCHES
    # ==========================================
    
    find_json = PythonOperator(
        task_id="find_latest_json",
        python_callable=find_latest_json,
        doc_md="""
        ### Recherche du fichier JSON
        Identifie le fichier JSON le plus récent dans `/include/youtube_data/`
        """,
    )
    
    sync_staging = PythonOperator(
        task_id="sync_to_staging",
        python_callable=sync_to_staging,
        doc_md="""
        ### Synchronisation vers Staging
        - UPSERT: Insertion/mise à jour des vidéos
        - DELETE: Suppression des vidéos obsolètes
        - Garantie d'unicité des video_ids
        """,
    )
    
    transform = PythonOperator(
        task_id="transform_to_core",
        python_callable=transform_to_core,
        doc_md="""
        ### Transformation vers Core
        - Conversion ISO 8601 → PostgreSQL INTERVAL
        - Labellisation: 'short' (<1 min) / 'long' (≥1 min)
        - Historique des statistiques
        """,
    )
    
    trigger_quality = TriggerDagRunOperator(
        task_id="trigger_data_quality",
        trigger_dag_id="data_quality",
        wait_for_completion=False,
        doc_md="""
        ### Déclenchement des contrôles qualité
        Lance automatiquement le DAG `data_quality` avec Soda Core
        """,
    )
    
    # ==========================================
    # 🔗 WORKFLOW
    # ==========================================
    find_json >> sync_staging >> transform >> trigger_quality
