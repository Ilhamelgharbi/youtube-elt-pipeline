from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from datetime import datetime, timedelta
import os
import json
import logging
from googleapiclient.discovery import build
import isodate

# ==========================================
# 🔑 CONFIGURATION - Reading from .env
# ==========================================
API_KEY = os.getenv("YOUTUBE_API_KEY")
CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID")
CHANNEL_HANDLE = os.getenv("YOUTUBE_CHANNEL_HANDLE", "MrBeast")
# Note: MAX_VIDEOS is no longer used - we extract ALL videos automatically!


def iso_duration_to_readable(duration):
    """Convert ISO 8601 duration to readable format (HH:MM:SS or MM:SS)"""
    try:
        td = isodate.parse_duration(duration)
        total_seconds = int(td.total_seconds())
        minutes, seconds = divmod(total_seconds, 60)
        hours, minutes = divmod(minutes, 60)
        return f"{hours}:{minutes:02d}:{seconds:02d}" if hours > 0 else f"{minutes}:{seconds:02d}"
    except:
        return "0:00"


def get_channel_videos(**context):
    """
    Extract ALL YouTube channel videos automatically
    - Detects total video count from channel statistics
    - Handles pagination automatically (50 videos per page)
    - Prevents duplicates using set()
    - Batches API requests efficiently
    """
    
    # Initialize YouTube client
    youtube = build("youtube", "v3", developerKey=API_KEY)
    logging.info(f"🚀 Starting extraction for channel: {CHANNEL_HANDLE} (ID: {CHANNEL_ID})")
    
    # ==========================================
    # 1️⃣ Get channel info (total videos + uploads playlist)
    # ==========================================
    request = youtube.channels().list(
        part="contentDetails,statistics",  # ✅ Added statistics to get video count
        id=CHANNEL_ID
    )
    response = request.execute()
    
    if not response["items"]:
        raise ValueError(f"❌ Channel not found: {CHANNEL_ID}")
    
    channel_data = response["items"][0]
    uploads_playlist = channel_data["contentDetails"]["relatedPlaylists"]["uploads"]
    total_videos_in_channel = int(channel_data["statistics"]["videoCount"])
    
    logging.info(f"✅ Found uploads playlist: {uploads_playlist}")
    logging.info(f"📊 Total videos in channel: {total_videos_in_channel}")
    logging.info(f"🎯 Will extract ALL {total_videos_in_channel} videos...")

    # ==========================================
    # 2️⃣ Collect ALL video IDs with pagination
    # ==========================================
    video_ids = set()  # Use set to prevent duplicates automatically!
    next_page_token = None
    page_count = 0
    
    # Loop until we have all videos from the channel
    while len(video_ids) < total_videos_in_channel:
        # Request next page of videos (max 50 per page)
        request = youtube.playlistItems().list(
            part="contentDetails",
            playlistId=uploads_playlist,
            maxResults=50,  # YouTube API max per request
            pageToken=next_page_token
        )
        response = request.execute()
        
        # Add video IDs to set (duplicates automatically ignored)
        new_ids = [item["contentDetails"]["videoId"] for item in response["items"]]
        video_ids.update(new_ids)
        
        page_count += 1
        logging.info(f"📄 Page {page_count}: Found {len(new_ids)} videos (Total: {len(video_ids)}/{total_videos_in_channel})")
        
        # Check if no more pages
        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            logging.info(f"✅ Reached end of playlist (no more pages)")
            break
    
    # Convert set to list
    video_ids = list(video_ids)
    logging.info(f"✅ Collected {len(video_ids)} unique video IDs from channel")

    # ==========================================
    # 3️⃣ Get video details in batches of 50
    # ==========================================
    videos = []
    
    for i in range(0, len(video_ids), 50):
        batch_ids = video_ids[i:i+50]
        batch_num = (i // 50) + 1
        
        logging.info(f"📦 Batch {batch_num}: Fetching details for {len(batch_ids)} videos...")
        
        request = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=",".join(batch_ids)
        )
        videos_response = request.execute()
        
        # Extract video data
        for video in videos_response["items"]:
            duration = video["contentDetails"]["duration"]
            videos.append({
                "video_id": video["id"],
                "title": video["snippet"]["title"],
                "published_at": video["snippet"]["publishedAt"],
                "duration": duration,
                "duration_readable": iso_duration_to_readable(duration),
                "view_count": video["statistics"].get("viewCount"),
                "like_count": video["statistics"].get("likeCount"),
                "comment_count": video["statistics"].get("commentCount"),
            })
    
    logging.info(f"✅ Extracted details for {len(videos)} videos")

    # ==========================================
    # 4️⃣ Prepare output data
    # ==========================================
    output = {
        "channel_handle": CHANNEL_HANDLE,
        "channel_id": CHANNEL_ID,
        "extraction_date": datetime.now().isoformat(),
        "total_videos": len(videos),
        "videos": videos
    }

    # ==========================================
    # 5️⃣ Save to JSON file
    # ==========================================
    data_path = "/usr/local/airflow/include/youtube_data"
    os.makedirs(data_path, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = os.path.join(data_path, f"{CHANNEL_HANDLE}_{timestamp}.json")
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=4, ensure_ascii=False)

    logging.info(f"✅ Saved {len(videos)} videos → {filename}")
    
    # Push to XCom for downstream tasks
    context['task_instance'].xcom_push(key='json_filename', value=filename)
    context['task_instance'].xcom_push(key='video_count', value=len(videos))
    
    return filename


# ==========================================
# 🎯 CONFIGURATION DU DAG
# ==========================================

# Arguments par défaut pour le DAG
default_args = {
    "owner": "airflow",                    # Propriétaire du DAG
    "depends_on_past": False,              # Ne dépend pas des exécutions précédentes
    "start_date": datetime(2025, 9, 1),    # Date de début
    "email_on_failure": False,             # Pas d'email en cas d'échec
    "email_on_retry": False,               # Pas d'email lors d'un retry
    "retries": 2,                          # 2 tentatives en cas d'erreur
    "retry_delay": timedelta(minutes=5),   # Attendre 5 minutes avant de réessayer
}

# ==========================================
# 📋 CRÉATION DU DAG
# ==========================================

with DAG(
    # Informations de base
    dag_id="produce_JSON",                              # Nom du DAG
    description="📥 Extraction des données YouTube → JSON",  # Description
    
    # Configuration
    default_args=default_args,
    schedule="0 14 * * *",                              # Tous les jours à 14h00
    catchup=False,                                      # Ne pas rattraper les exécutions passées
    max_active_runs=1,                                  # Une seule exécution à la fois
    
    # Tags pour filtrer dans l'interface
    tags=["youtube", "extraction", "json", "beginner"],
    
    # Documentation (visible dans l'interface Airflow)
    doc_md="""
    # 📺 DAG d'Extraction YouTube
    
    ## 🎯 Objectif
    Extraire les données des vidéos de la chaîne **MrBeast** et les sauvegarder en JSON.
    
    ## 📊 Données extraites
    - ID de la vidéo
    - Titre
    - Date de publication
    - Durée (format ISO et lisible)
    - Nombre de vues
    - Nombre de likes
    - Nombre de commentaires
    - URL de la miniature
    
    ## 📁 Fichiers de sortie
    - Format: `MrBeast_YYYYMMDD_HHMMSS.json`
    - Emplacement: `/opt/airflow/include/youtube_data/`
    
    ## 📅 Planification
    - **Fréquence**: Quotidienne
    - **Heure**: 14h00 (2 PM)
    
    ## 🔄 Retry
    - **Tentatives**: 2
    - **Délai**: 5 minutes
    
    ## 📌 Notes
    - Quota API YouTube: ~3 unités par exécution (avec 50 vidéos)
    - Limite quotidienne: 10,000 unités
    """,
    
) as dag:
    
    # ==========================================
    # 📋 DÉFINITION DES TÂCHES
    # ==========================================
    
    # TÂCHE 1: Extraire les données YouTube et sauvegarder en JSON
    extract_task = PythonOperator(
        task_id="extract_youtube_videos",
        python_callable=get_channel_videos,
        doc_md="""
        ### 📥 Extraction des Vidéos YouTube
        
        Cette tâche fait tout le travail d'extraction:
        1. ✅ Se connecte à l'API YouTube avec la clé API
        2. ✅ Récupère les vidéos de la chaîne MrBeast
        3. ✅ Extrait toutes les métadonnées importantes
        4. ✅ Nettoie et structure les données
        5. ✅ Sauvegarde dans un fichier JSON horodaté
        
        **Sortie**: Fichier JSON dans `include/youtube_data/`
        
        **Quota API utilisé**: ~3 unités (1 pour channel + 1 pour playlist + 1 pour videos)
        """,
    )
    
    # TÂCHE 2: Déclencher le DAG de chargement
    trigger_load = TriggerDagRunOperator(
        task_id="trigger_update_db",
        trigger_dag_id="update_db",
        wait_for_completion=False,
        doc_md="""
        ### 🔗 Déclenchement du DAG update_db
        
        Cette tâche déclenche automatiquement le DAG `update_db` après l'extraction.
        
        **Workflow complet**:
        1. ✅ produce_JSON: Extraction → JSON
        2. ✅ update_db: JSON → PostgreSQL (staging + core)
        3. ✅ data_quality: Validation Soda Core
        """,
    )
    
    # ==========================================
    # 🔗 DÉPENDANCES DES TÂCHES
    # ==========================================
    
    # Workflow: Extract → Trigger Load
    extract_task >> trigger_load


# ==========================================
# 💡 COMMENT UTILISER CE DAG
# ==========================================
"""
1️⃣ Démarrer Airflow:
   astro dev start

2️⃣ Ouvrir l'interface:
   http://localhost:8080
   Username: admin
   Password: admin

3️⃣ Trouver le DAG "produce_JSON"

4️⃣ Activer le DAG (toggle ON)

5️⃣ Déclencher manuellement:
   Cliquer sur le bouton ▶️ "Trigger DAG"

6️⃣ Voir les logs:
   Cliquer sur la tâche → Logs

7️⃣ Vérifier le fichier JSON:
   include/youtube_data/MrBeast_YYYYMMDD_HHMMSS.json

8️⃣ Tester via CLI:
   astro dev bash
   airflow dags test produce_JSON 2025-10-02
   exit
"""
