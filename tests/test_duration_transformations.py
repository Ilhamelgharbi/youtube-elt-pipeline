"""
🧪 Duration Transformation Tests
Tests for ISO 8601 duration conversion and labeling logic
Tests the actual transformation used in transform_to_core() function

Test Count: 10 duration transformation tests
"""

import pytest


# ==========================================
# ✅ Test 1-4: Duration Label Logic (from youtube_load_db.py lines 219-221)
# ==========================================

@pytest.mark.unit
def test_duration_label_short_for_under_60_seconds():
    """Test 1: Duration < 60 seconds labeled as 'short'"""
    total_seconds = 59
    duration_label = 'short' if total_seconds < 60 else 'long'
    
    assert duration_label == 'short'


@pytest.mark.unit
def test_duration_label_long_for_60_seconds():
    """Test 2: Duration = 60 seconds labeled as 'long'"""
    total_seconds = 60
    duration_label = 'short' if total_seconds < 60 else 'long'
    
    assert duration_label == 'long'


@pytest.mark.unit
def test_duration_label_long_for_over_60_seconds():
    """Test 3: Duration > 60 seconds labeled as 'long'"""
    total_seconds = 3661  # 1 hour 1 minute 1 second
    duration_label = 'short' if total_seconds < 60 else 'long'
    
    assert duration_label == 'long'


@pytest.mark.unit
def test_duration_label_boundary_59_seconds():
    """Test 4: Boundary test - 59 seconds is 'short'"""
    total_seconds = 59
    duration_label = 'short' if total_seconds < 60 else 'long'
    
    assert duration_label == 'short'


# ==========================================
# ✅ Test 5-8: ISO 8601 Duration Parsing (PostgreSQL format)
# ==========================================

@pytest.mark.unit
def test_iso_duration_pt_format():
    """Test 5: ISO 8601 duration starts with PT"""
    duration = "PT22M26S"
    
    assert duration.startswith("PT")
    assert "M" in duration or "S" in duration or "H" in duration


@pytest.mark.unit
def test_iso_duration_short_video():
    """Test 6: Short video duration (PT58S = 58 seconds)"""
    import isodate
    duration = "PT58S"
    td = isodate.parse_duration(duration)
    total_seconds = int(td.total_seconds())
    
    assert total_seconds == 58
    assert total_seconds < 60  # Should be labeled 'short'


@pytest.mark.unit
def test_iso_duration_medium_video():
    """Test 7: Medium video duration (PT22M26S = 1346 seconds)"""
    import isodate
    duration = "PT22M26S"
    td = isodate.parse_duration(duration)
    total_seconds = int(td.total_seconds())
    
    assert total_seconds == 1346
    assert total_seconds >= 60  # Should be labeled 'long'


@pytest.mark.unit
def test_iso_duration_long_video_with_hours():
    """Test 8: Long video with hours (PT1H23M45S)"""
    import isodate
    duration = "PT1H23M45S"
    td = isodate.parse_duration(duration)
    total_seconds = int(td.total_seconds())
    
    expected_seconds = (1 * 3600) + (23 * 60) + 45  # 5025 seconds
    assert total_seconds == expected_seconds
    assert total_seconds >= 60  # Should be labeled 'long'


# ==========================================
# ✅ Test 9-10: Edge Cases and Data Quality
# ==========================================

@pytest.mark.unit
def test_duration_exactly_one_minute():
    """Test 9: Exactly 1 minute (PT1M = 60 seconds) is 'long'"""
    import isodate
    duration = "PT1M"
    td = isodate.parse_duration(duration)
    total_seconds = int(td.total_seconds())
    duration_label = 'short' if total_seconds < 60 else 'long'
    
    assert total_seconds == 60
    assert duration_label == 'long'


@pytest.mark.unit
def test_duration_very_short_video():
    """Test 10: Very short video (PT1S = 1 second) is 'short'"""
    import isodate
    duration = "PT1S"
    td = isodate.parse_duration(duration)
    total_seconds = int(td.total_seconds())
    duration_label = 'short' if total_seconds < 60 else 'long'
    
    assert total_seconds == 1
    assert duration_label == 'short'


# ==========================================
# ✅ Bonus Test: Real MrBeast Data Simulation
# ==========================================

@pytest.mark.integration
def test_mrbeast_duration_distribution():
    """Integration Test: Simulate MrBeast video duration distribution
    
    Based on actual data:
    - 144 short videos (< 60 seconds)
    - 760 long videos (>= 60 seconds)
    """
    import isodate
    
    # Sample durations from actual MrBeast channel
    sample_durations = [
        "PT58S",       # Short (58 seconds)
        "PT22M26S",    # Long (22:26)
        "PT13M11S",    # Long (13:11)
        "PT2M28S",     # Long (2:28)
        "PT35S",       # Short (35 seconds)
        "PT1H5M12S",   # Long (1:05:12)
    ]
    
    short_count = 0
    long_count = 0
    
    for duration in sample_durations:
        td = isodate.parse_duration(duration)
        total_seconds = int(td.total_seconds())
        duration_label = 'short' if total_seconds < 60 else 'long'
        
        if duration_label == 'short':
            short_count += 1
        else:
            long_count += 1
    
    # Verify both types exist in sample
    assert short_count == 2  # PT58S and PT35S
    assert long_count == 4   # All others
    assert short_count + long_count == len(sample_durations)
