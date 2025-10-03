"""
🧪 Unit Tests - Helper Functions
Simple tests for utility functions in the YouTube ELT pipeline

Test Count: 8 unit tests
"""

import pytest
import isodate


# ==========================================
# 🔧 Helper Function (copied from DAG)
# ==========================================

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


# ==========================================
# ✅ Test 1-5: ISO Duration Conversion
# ==========================================

@pytest.mark.unit
def test_iso_duration_minutes_seconds():
    """Test 1: Convert PT37M4S to 37:04"""
    result = iso_duration_to_readable("PT37M4S")
    assert result == "37:04"


@pytest.mark.unit
def test_iso_duration_seconds_only():
    """Test 2: Convert PT35S to 0:35"""
    result = iso_duration_to_readable("PT35S")
    assert result == "0:35"


@pytest.mark.unit
def test_iso_duration_with_hours():
    """Test 3: Convert PT1H23M45S to 1:23:45"""
    result = iso_duration_to_readable("PT1H23M45S")
    assert result == "1:23:45"


@pytest.mark.unit
def test_iso_duration_minutes_only():
    """Test 4: Convert PT5M to 5:00"""
    result = iso_duration_to_readable("PT5M")
    assert result == "5:00"


@pytest.mark.unit
def test_iso_duration_hours_only():
    """Test 5: Convert PT2H to 2:00:00"""
    result = iso_duration_to_readable("PT2H")
    assert result == "2:00:00"


# ==========================================
# ✅ Test 6: Invalid Duration Handling
# ==========================================

@pytest.mark.unit
def test_iso_duration_invalid_format():
    """Test 6: Invalid duration returns default 0:00"""
    result = iso_duration_to_readable("INVALID")
    assert result == "0:00"


# ==========================================
# ✅ Test 7-8: Data Validation
# ==========================================

@pytest.mark.unit
def test_video_data_has_required_fields(sample_video_data):
    """Test 7: Video data contains all required fields"""
    required_fields = [
        "video_id", "title", "published_at", "duration",
        "view_count", "like_count", "comment_count"
    ]
    
    for field in required_fields:
        assert field in sample_video_data, f"Missing required field: {field}"


@pytest.mark.unit
def test_json_output_structure(sample_json_output):
    """Test 8: JSON output has correct structure"""
    # Check top-level fields
    assert "channel_handle" in sample_json_output
    assert "extraction_date" in sample_json_output
    assert "total_videos" in sample_json_output
    assert "videos" in sample_json_output
    
    # Check videos is a list
    assert isinstance(sample_json_output["videos"], list)
    
    # Check total_videos matches actual count
    assert sample_json_output["total_videos"] == len(sample_json_output["videos"])


# ==========================================
# 📊 Test Summary
# ==========================================
"""
✅ UNIT TESTS SUMMARY (8 tests):

1. test_iso_duration_minutes_seconds - PT37M4S → 37:04
2. test_iso_duration_seconds_only - PT35S → 0:35
3. test_iso_duration_with_hours - PT1H23M45S → 1:23:45
4. test_iso_duration_minutes_only - PT5M → 5:00
5. test_iso_duration_hours_only - PT2H → 2:00:00
6. test_iso_duration_invalid_format - Invalid input handling
7. test_video_data_has_required_fields - Required fields validation
8. test_json_output_structure - JSON structure validation

Total: 8/20 tests complete
"""
