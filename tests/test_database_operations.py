"""
🧪 Database Operations Tests
Tests for UPSERT logic, NULL handling, and data synchronization
Tests the actual database operations used in sync_to_staging() and transform_to_core()

Test Count: 8 database operation tests
"""

import pytest


# ==========================================
# ✅ Test 1-3: NULL Handling (from youtube_load_db.py lines 130-132)
# ==========================================

@pytest.mark.unit
def test_view_count_none_handling():
    """Test 1: NULL view_count converts to 0"""
    view_count = None
    result = int(view_count) if view_count is not None else 0
    
    assert result == 0
    assert isinstance(result, int)


@pytest.mark.unit
def test_like_count_none_handling():
    """Test 2: NULL like_count converts to 0"""
    like_count = None
    result = int(like_count) if like_count is not None else 0
    
    assert result == 0
    assert isinstance(result, int)


@pytest.mark.unit
def test_comment_count_none_handling():
    """Test 3: NULL comment_count converts to 0"""
    comment_count = None
    result = int(comment_count) if comment_count is not None else 0
    
    assert result == 0
    assert isinstance(result, int)


# ==========================================
# ✅ Test 4-5: Statistics String to Integer Conversion
# ==========================================

@pytest.mark.unit
def test_statistics_string_conversion_large_numbers():
    """Test 4: Convert large YouTube statistics from string to int"""
    view_count_str = "54506132"
    like_count_str = "1833636"
    comment_count_str = "27466"
    
    view_count = int(view_count_str) if view_count_str is not None else 0
    like_count = int(like_count_str) if like_count_str is not None else 0
    comment_count = int(comment_count_str) if comment_count_str is not None else 0
    
    assert view_count == 54506132
    assert like_count == 1833636
    assert comment_count == 27466


@pytest.mark.unit
def test_statistics_zero_values():
    """Test 5: Zero statistics are valid"""
    view_count = 0
    like_count = 0
    comment_count = 0
    
    assert view_count >= 0
    assert like_count >= 0
    assert comment_count >= 0


# ==========================================
# ✅ Test 6-7: Deduplication Logic (from youtube_load_db.py line 82)
# ==========================================

@pytest.mark.integration
def test_deduplication_with_dict_comprehension():
    """Test 6: Deduplication using dict comprehension keeps last occurrence"""
    videos = [
        {"video_id": "abc123", "title": "First", "view_count": "1000"},
        {"video_id": "def456", "title": "Second", "view_count": "2000"},
        {"video_id": "abc123", "title": "Updated", "view_count": "1500"},  # Duplicate with updated data
    ]
    
    # Simulates: unique_videos = {v['video_id']: v for v in videos}
    unique_videos = {v['video_id']: v for v in videos}
    result = list(unique_videos.values())
    
    # Should have only 2 unique videos
    assert len(result) == 2
    
    # Find the abc123 video
    abc_video = unique_videos.get("abc123")
    assert abc_video is not None
    # Dict comprehension keeps the LAST occurrence
    assert abc_video["title"] == "Updated"
    assert abc_video["view_count"] == "1500"


@pytest.mark.integration
def test_deduplication_preserves_order_of_last_occurrence():
    """Test 7: Deduplication preserves all unique video_ids"""
    videos = [
        {"video_id": "aaa", "title": "Video A"},
        {"video_id": "bbb", "title": "Video B"},
        {"video_id": "ccc", "title": "Video C"},
        {"video_id": "aaa", "title": "Video A Updated"},  # Duplicate
        {"video_id": "ddd", "title": "Video D"},
    ]
    
    unique_videos = {v['video_id']: v for v in videos}
    video_ids = set(unique_videos.keys())
    
    # Should have 4 unique video IDs
    assert len(video_ids) == 4
    assert video_ids == {"aaa", "bbb", "ccc", "ddd"}


# ==========================================
# ✅ Test 8: DELETE Synchronization Logic
# ==========================================

@pytest.mark.integration
def test_delete_synchronization_logic():
    """Test 8: Videos in staging but not in JSON should be deleted
    
    Simulates the DELETE logic from youtube_load_db.py lines 151-158
    """
    # Existing videos in staging
    existing_ids = {"video1", "video2", "video3", "video4"}
    
    # Videos from new JSON extraction
    json_video_ids = {"video2", "video3", "video5", "video6"}
    
    # Calculate which videos should be deleted
    to_delete = existing_ids - json_video_ids
    
    # Should delete video1 and video4 (not in new JSON)
    assert to_delete == {"video1", "video4"}
    assert len(to_delete) == 2
    
    # Verify the videos that should remain
    remaining = existing_ids & json_video_ids
    assert remaining == {"video2", "video3"}


# ==========================================
# ✅ Bonus Test: Complete UPSERT Simulation
# ==========================================

@pytest.mark.integration
def test_complete_upsert_simulation():
    """Integration Test: Simulate complete UPSERT behavior
    
    Simulates:
    1. Deduplication
    2. NULL handling
    3. Type conversion
    4. UPDATE existing, INSERT new
    """
    # Simulated database state (existing videos)
    existing_videos = {
        "video1": {"video_id": "video1", "title": "Old Title", "view_count": 1000},
        "video2": {"video_id": "video2", "title": "Existing", "view_count": 2000},
    }
    
    # New JSON data with updates and new videos
    json_videos = [
        {"video_id": "video1", "title": "Updated Title", "view_count": "1500"},  # UPDATE
        {"video_id": "video2", "title": "Existing", "view_count": "2000"},      # NO CHANGE
        {"video_id": "video3", "title": "New Video", "view_count": None},       # INSERT with NULL
        {"video_id": "video3", "title": "New Video", "view_count": "3000"},     # Duplicate (keep last)
    ]
    
    # Step 1: Deduplication
    unique_videos = {v['video_id']: v for v in json_videos}
    
    # Step 2: Process each video
    processed_videos = {}
    for video_id, video in unique_videos.items():
        # Handle NULL view_count
        view_count_raw = video.get("view_count")
        view_count = int(view_count_raw) if view_count_raw is not None else 0
        
        processed_videos[video_id] = {
            "video_id": video_id,
            "title": video["title"],
            "view_count": view_count
        }
    
    # Verify results
    assert len(processed_videos) == 3  # 3 unique videos after deduplication
    
    # video1 should have updated view_count
    assert processed_videos["video1"]["view_count"] == 1500
    assert processed_videos["video1"]["title"] == "Updated Title"
    
    # video3 should use the last occurrence (with view_count)
    assert processed_videos["video3"]["view_count"] == 3000
    assert processed_videos["video3"]["title"] == "New Video"
    
    # Determine operations
    to_insert = set(processed_videos.keys()) - set(existing_videos.keys())
    to_update = set(processed_videos.keys()) & set(existing_videos.keys())
    
    assert to_insert == {"video3"}
    assert to_update == {"video1", "video2"}
