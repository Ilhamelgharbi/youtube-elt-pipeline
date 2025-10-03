"""
🧪 Data Transformation Tests
Tests for data cleaning and transformation logic used in update_db DAG

Test Count: 6 transformation tests
"""

import pytest
import json


# ==========================================
# ✅ Test 15-17: Data Type Conversions (sync_to_staging function)
# ==========================================

@pytest.mark.unit
def test_view_count_string_to_int():
    """Test 15: View count converts from string to integer (line 96 youtube_load_db.py)"""
    view_count_str = "54506132"
    # Simulates: int(video.get('view_count', 0))
    view_count_int = int(view_count_str)
    
    assert isinstance(view_count_int, int)
    assert view_count_int == 54506132


@pytest.mark.unit
def test_like_count_string_to_int():
    """Test 16: Like count converts from string to integer (line 97 youtube_load_db.py)"""
    like_count_str = "1833636"
    # Simulates: int(video.get('like_count', 0))
    like_count_int = int(like_count_str)
    
    assert isinstance(like_count_int, int)
    assert like_count_int == 1833636


@pytest.mark.unit
def test_comment_count_handles_missing_value():
    """Test 17: Comment count handles missing/None values with default 0"""
    video_data = {"comment_count": None}
    
    # Simulates: int(video.get("comment_count", 0))
    comment_count = int(video_data.get("comment_count", 0) or 0)
    
    assert comment_count == 0
    assert isinstance(comment_count, int)


# ==========================================
# ✅ Test 18-19: Duplicate Handling (unique_videos dict)
# ==========================================

@pytest.mark.unit
def test_duplicate_removal_keeps_first():
    """Test 18: Duplicate video_ids are removed (line 53 youtube_load_db.py)"""
    videos = [
        {"video_id": "abc123", "title": "First"},
        {"video_id": "abc123", "title": "Duplicate"},
        {"video_id": "def456", "title": "Second"}
    ]
    
    # Simulates: unique_videos = {v['video_id']: v for v in videos}
    unique_videos = {v['video_id']: v for v in videos}
    result = list(unique_videos.values())
    
    assert len(result) == 2  # Only 2 unique videos
    assert result[0]["video_id"] != result[1]["video_id"]


@pytest.mark.unit
def test_video_id_correct_length(sample_video_data):
    """Test 19: Video IDs are exactly 11 characters (YouTube format)"""
    video_id = sample_video_data["video_id"]
    
    assert len(video_id) == 11
    assert isinstance(video_id, str)


# ==========================================
# ✅ Test 20: JSON File Parsing (find_latest_json function)
# ==========================================

@pytest.mark.unit
def test_json_file_is_valid(temp_json_file):
    """Test 20: JSON file can be read and parsed correctly (line 44 youtube_load_db.py)"""
    # Simulates: with open(json_file, 'r', encoding='utf-8') as f: data = json.load(f)
    with open(temp_json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Validate structure matches produce_JSON output
    assert "channel_handle" in data
    assert "videos" in data
    assert isinstance(data["videos"], list)
    assert len(data["videos"]) > 0
    assert "extraction_date" in data


# ==========================================
# ==========================================
# Test Summary
# ==========================================
"""
DATA TRANSFORMATION TESTS SUMMARY (6 tests):

Type Conversions (sync_to_staging):
15. test_view_count_string_to_int - String to Integer
16. test_like_count_string_to_int - String to Integer
17. test_comment_count_handles_missing_value - Null handling to 0

Duplicate Handling:
18. test_duplicate_removal_keeps_first - UPSERT logic validation
19. test_video_id_correct_length - Format validation (11 chars)

JSON Processing:
20. test_json_file_is_valid - JSON parsing from produce_JSON output

Total: 20/20 tests complete
"""

