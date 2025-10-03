#!/usr/bin/env python3
"""
Test Duration Transformation Logic
Validates ISO 8601 → INTERVAL conversion and duration labels
"""

import re

def iso_to_seconds(duration):
    """
    Convert ISO 8601 duration to seconds
    Example: PT22M26S → 1346 seconds
    """
    if not duration or not duration.startswith('PT'):
        return 0
    
    # Remove PT prefix
    duration = duration[2:]
    
    hours = 0
    minutes = 0
    seconds = 0
    
    # Extract hours
    h_match = re.search(r'(\d+)H', duration)
    if h_match:
        hours = int(h_match.group(1))
    
    # Extract minutes
    m_match = re.search(r'(\d+)M', duration)
    if m_match:
        minutes = int(m_match.group(1))
    
    # Extract seconds
    s_match = re.search(r'(\d+)S', duration)
    if s_match:
        seconds = int(s_match.group(1))
    
    total = (hours * 3600) + (minutes * 60) + seconds
    return total


def get_duration_label(seconds):
    """
    Get duration label based on seconds
    < 60 seconds = 'short'
    >= 60 seconds = 'long'
    """
    return 'short' if seconds < 60 else 'long'


def format_interval(seconds):
    """
    Format seconds as HH:MM:SS interval
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


# Test cases
test_cases = [
    ("PT15S", "0:15", 15, "short"),
    ("PT35S", "0:35", 35, "short"),
    ("PT52S", "0:52", 52, "short"),
    ("PT59S", "0:59", 59, "short"),
    ("PT1M", "1:00", 60, "long"),
    ("PT1M1S", "1:01", 61, "long"),
    ("PT22M26S", "22:26", 1346, "long"),
    ("PT40M2S", "40:02", 2402, "long"),
    ("PT1H15M3S", "1:15:03", 4503, "long"),
    ("PT2H", "2:00:00", 7200, "long"),
]

print("=" * 80)
print("DURATION TRANSFORMATION VERIFICATION")
print("=" * 80)
print()

all_passed = True

for iso_duration, readable, expected_seconds, expected_label in test_cases:
    actual_seconds = iso_to_seconds(iso_duration)
    actual_label = get_duration_label(actual_seconds)
    actual_interval = format_interval(actual_seconds)
    
    passed = (actual_seconds == expected_seconds and actual_label == expected_label)
    status = "✅ PASS" if passed else "❌ FAIL"
    
    if not passed:
        all_passed = False
    
    print(f"{status} | {iso_duration:12} → {actual_seconds:5}s | {actual_interval:10} | {actual_label:5} | Expected: {expected_label}")

print()
print("=" * 80)

if all_passed:
    print("✅ ALL TESTS PASSED - Duration transformation logic is correct!")
else:
    print("❌ SOME TESTS FAILED - Check logic!")

print("=" * 80)
print()
print("SQL Transformation Flow:")
print("1. ISO 8601 (PT22M26S) → regexp_replace → '22 minutes 26 seconds'")
print("2. Cast to INTERVAL → PostgreSQL INTERVAL type")
print("3. EXTRACT(EPOCH) → total seconds (1346)")
print("4. Compare with 60 → label = 'long'")
print("5. Convert back to INTERVAL for storage → '00:22:26'")
print()
print("Threshold: 60 seconds (1 minute)")
print("  - short: < 60 seconds")
print("  - long:  >= 60 seconds")
print()
