"""
🧪 Pytest Configuration and Fixtures
Simple test helpers for YouTube ELT Pipeline
"""

import pytest
import os
from datetime import datetime
from pathlib import Path


# ==========================================
# 📂 Test Data Fixtures
# ==========================================

@pytest.fixture
def sample_video_data():
    """Sample video data for testing (like what YouTube API returns)"""
    return {
        "video_id": "4l97aNza_Zc",
        "title": "Survive 30 Days Chained To Your Ex, Win $250,000",
        "published_at": "2025-09-13T16:00:01Z",
        "duration": "PT37M4S",  # ISO 8601 format
        "view_count": "54506132",
        "like_count": "1833636",
        "comment_count": "27466",
        "channel_id": "UCX6OQ3DkcsbYNE6H8uQQuVA",
        "channel_handle": "MrBeast"
    }


@pytest.fixture
def sample_json_output():
    """Sample complete JSON output from produce_JSON DAG"""
    return {
        "channel_handle": "MrBeast",
        "channel_id": "UCX6OQ3DkcsbYNE6H8uQQuVA",
        "extraction_date": "2025-10-02T14:30:00.123456",
        "total_videos": 2,
        "videos": [
            {
                "video_id": "4l97aNza_Zc",
                "title": "Survive 30 Days Chained To Your Ex",
                "published_at": "2025-09-13T16:00:01Z",
                "duration": "PT37M4S",
                "duration_readable": "37:04",
                "view_count": "54506132",
                "like_count": "1833636",
                "comment_count": "27466"
            },
            {
                "video_id": "3ih2bPKSWsQ",
                "title": "I Arrested IShowSpeed",
                "published_at": "2025-09-12T17:00:01Z",
                "duration": "PT35S",
                "duration_readable": "0:35",
                "view_count": "30850222",
                "like_count": "1058130",
                "comment_count": "3265"
            }
        ]
    }


@pytest.fixture
def temp_json_file(tmp_path, sample_json_output):
    """Create a temporary JSON file for testing"""
    import json
    
    json_file = tmp_path / "MrBeast_20251002_143000.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(sample_json_output, f, indent=4)
    
    return json_file


# ==========================================
# 📅 Date/Time Fixtures
# ==========================================

@pytest.fixture
def iso_durations():
    """Sample ISO 8601 durations for testing"""
    return {
        "PT37M4S": "37:04",      # 37 minutes 4 seconds
        "PT35S": "0:35",          # 35 seconds
        "PT1H23M45S": "1:23:45",  # 1 hour 23 minutes 45 seconds
        "PT5M": "5:00",           # 5 minutes
        "PT2H": "2:00:00",        # 2 hours
    }


# ==========================================
# 🗄️ Database Fixtures (for future integration tests)
# ==========================================

@pytest.fixture
def mock_postgres_connection():
    """Mock PostgreSQL connection for testing"""
    # This would be expanded for actual database tests
    return {
        "host": "localhost",
        "port": 5432,
        "database": "youtube_dwh",
        "user": "postgres",
        "password": "postgres"
    }


# ==========================================
# 📁 File System Fixtures
# ==========================================

@pytest.fixture
def mock_data_directory(tmp_path):
    """Create a temporary data directory structure"""
    data_dir = tmp_path / "youtube_data"
    data_dir.mkdir()
    return data_dir
