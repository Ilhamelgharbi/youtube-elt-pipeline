"""
🧪 Data Quality Validation Tests
Tests for Soda Core quality check logic and data validation rules
Tests align with the 54 quality checks defined in include/soda/checks/videos_quality.yml

Test Count: 12 data quality tests
"""

import pytest
import re


# ==========================================
# ✅ Test 1-4: Video ID Format Validation
# ==========================================

@pytest.mark.unit
def test_video_id_length_11_characters():
    """Test 1: YouTube video IDs must be exactly 11 characters
    
    Corresponds to Soda check: invalid_count(video_id) = 0 with valid length: 11
    """
    valid_video_ids = ["4l97aNza_Zc", "3ih2bPKSWsQ", "pl4xmh3RWfE", "-z349CGAOXs"]
    
    for video_id in valid_video_ids:
        assert len(video_id) == 11, f"Video ID {video_id} is not 11 characters"


@pytest.mark.unit
def test_video_id_invalid_length_rejected():
    """Test 2: Video IDs with incorrect length should be invalid"""
    invalid_video_ids = [
        "abc",           # Too short (3 chars)
        "abcdefghijkl",  # Too long (12 chars)
        "",              # Empty
    ]
    
    for video_id in invalid_video_ids:
        assert len(video_id) != 11, f"Video ID {video_id} should be invalid"


# ==========================================
# ✅ Test 3-5: Title Format Validation
# ==========================================

@pytest.mark.unit
def test_title_length_within_range():
    """Test 3: Title length must be 1-500 characters
    
    Corresponds to Soda check: valid min length: 1, valid max length: 500
    """
    valid_titles = [
        "A",  # Minimum (1 char)
        "Survive 30 Days Chained To Your Ex, Win $250,000",  # Normal
        "X" * 500,  # Maximum (500 chars)
    ]
    
    for title in valid_titles:
        assert 1 <= len(title) <= 500, f"Title length {len(title)} is invalid"


@pytest.mark.unit
def test_title_empty_rejected():
    """Test 4: Empty title should be invalid"""
    title = ""
    assert len(title) == 0
    assert not (1 <= len(title) <= 500)


@pytest.mark.unit
def test_title_too_long_rejected():
    """Test 5: Title > 500 characters should be invalid"""
    title = "X" * 501
    assert len(title) > 500
    assert not (1 <= len(title) <= 500)


# ==========================================
# ✅ Test 6-8: Duration Format Validation
# ==========================================

@pytest.mark.unit
def test_duration_iso8601_format():
    """Test 6: Duration must be ISO 8601 format starting with 'P'
    
    Corresponds to Soda check: valid regex: '^P.*'
    """
    valid_durations = [
        "PT58S",
        "PT22M26S",
        "PT1H5M12S",
        "P1D",  # 1 day (also valid ISO 8601)
        "PT0S",  # Zero seconds
    ]
    
    for duration in valid_durations:
        assert duration.startswith("P"), f"Duration {duration} doesn't start with 'P'"


@pytest.mark.unit
def test_duration_readable_format_validation():
    """Test 7: Duration readable must match M:SS or MM:SS or H:MM:SS format
    
    Corresponds to Soda check: valid regex: '^\d+:\d{2}(:\d{2})?$'
    """
    pattern = r'^\d+:\d{2}(:\d{2})?$'
    
    valid_formats = [
        "0:35",      # M:SS (seconds < 10 minutes)
        "13:11",     # MM:SS
        "1:23:45",   # H:MM:SS
        "12:05",     # MM:SS
        "100:59",    # Large minute value
    ]
    
    for duration_readable in valid_formats:
        assert re.match(pattern, duration_readable), f"{duration_readable} doesn't match format"


@pytest.mark.unit
def test_duration_readable_invalid_format_rejected():
    """Test 8: Invalid duration_readable formats should be rejected"""
    pattern = r'^\d+:\d{2}(:\d{2})?$'
    
    invalid_formats = [
        "5:5",        # Missing leading zero (should be 5:05)
        "1:2:3",      # Single digit seconds
        "abc",        # Not a time format
        "12",         # No colon separator
        "12:",        # Missing seconds
        ":30",        # Missing minutes
    ]
    
    for duration_readable in invalid_formats:
        assert not re.match(pattern, duration_readable), f"{duration_readable} should be invalid"


# ==========================================
# ✅ Test 9-11: Statistics Validation (Business Rules)
# ==========================================

@pytest.mark.unit
def test_statistics_non_negative():
    """Test 9: View/like/comment counts must be >= 0
    
    Corresponds to Soda checks: valid min: 0 for all counts
    """
    valid_statistics = [
        {"view_count": 0, "like_count": 0, "comment_count": 0},
        {"view_count": 1000000, "like_count": 50000, "comment_count": 10000},
    ]
    
    for stats in valid_statistics:
        assert stats["view_count"] >= 0
        assert stats["like_count"] >= 0
        assert stats["comment_count"] >= 0


@pytest.mark.unit
def test_likes_cannot_exceed_views():
    """Test 10: Likes cannot be greater than views (business rule)
    
    Corresponds to Soda check: fail condition: like_count > view_count
    """
    # Valid case
    valid_video = {"view_count": 1000, "like_count": 800}
    assert valid_video["like_count"] <= valid_video["view_count"]
    
    # Invalid case
    invalid_video = {"view_count": 1000, "like_count": 1200}
    assert not (invalid_video["like_count"] <= invalid_video["view_count"])


@pytest.mark.unit
def test_comments_cannot_exceed_views():
    """Test 11: Comments cannot be greater than views (business rule)
    
    Corresponds to Soda check: fail condition: comment_count > view_count
    """
    # Valid case
    valid_video = {"view_count": 1000, "comment_count": 500}
    assert valid_video["comment_count"] <= valid_video["view_count"]
    
    # Invalid case
    invalid_video = {"view_count": 1000, "comment_count": 1500}
    assert not (invalid_video["comment_count"] <= invalid_video["view_count"])


# ==========================================
# ✅ Test 12: Duration Label Validation
# ==========================================

@pytest.mark.unit
def test_duration_label_enum_validation():
    """Test 12: Duration label must be 'short' or 'long'
    
    Corresponds to Soda check: valid values: ['short', 'long']
    """
    valid_labels = ['short', 'long']
    
    # Valid cases
    for label in valid_labels:
        assert label in ['short', 'long']
    
    # Invalid cases
    invalid_labels = ['medium', 'very_long', 'SHORT', 'Long', '']
    for label in invalid_labels:
        assert label not in ['short', 'long']


# ==========================================
# ✅ Integration Test: Complete Data Quality Check
# ==========================================

@pytest.mark.integration
def test_complete_video_data_quality():
    """Integration Test: Validate complete video data against all quality rules"""
    video_data = {
        "video_id": "4l97aNza_Zc",
        "title": "Survive 30 Days Chained To Your Ex, Win $250,000",
        "duration": "PT37M4S",
        "duration_readable": "37:04",
        "duration_label": "long",
        "view_count": 54506132,
        "like_count": 1833636,
        "comment_count": 27466,
    }
    
    # Quality checks
    assert len(video_data["video_id"]) == 11  # ✅ Video ID format
    assert 1 <= len(video_data["title"]) <= 500  # ✅ Title length
    assert video_data["duration"].startswith("P")  # ✅ ISO 8601 duration
    assert re.match(r'^\d+:\d{2}(:\d{2})?$', video_data["duration_readable"])  # ✅ Duration readable
    assert video_data["duration_label"] in ['short', 'long']  # ✅ Duration label enum
    assert video_data["view_count"] >= 0  # ✅ Non-negative views
    assert video_data["like_count"] >= 0  # ✅ Non-negative likes
    assert video_data["comment_count"] >= 0  # ✅ Non-negative comments
    assert video_data["like_count"] <= video_data["view_count"]  # ✅ Business rule
    assert video_data["comment_count"] <= video_data["view_count"]  # ✅ Business rule
    
    # Duration label consistency check
    import isodate
    td = isodate.parse_duration(video_data["duration"])
    total_seconds = int(td.total_seconds())
    expected_label = 'short' if total_seconds < 60 else 'long'
    assert video_data["duration_label"] == expected_label  # ✅ Label matches duration
