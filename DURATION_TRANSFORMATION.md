# 🕐 Duration Transformation Feature

## ✅ New Features Added

### **1. Duration as INTERVAL (duration_seconds)**
Converts ISO 8601 duration format to PostgreSQL INTERVAL type for easy calculations.

**Example:**
```
ISO 8601: PT22M26S  →  INTERVAL: 00:22:26  (22 minutes 26 seconds)
ISO 8601: PT52S     →  INTERVAL: 00:00:52  (52 seconds)
ISO 8601: PT1H15M3S →  INTERVAL: 01:15:03  (1 hour 15 minutes 3 seconds)
```

### **2. Duration Label (short/long)**
Automatically labels videos based on length:
- **"short"** = Less than 1 minute (< 60 seconds)
- **"long"** = 1 minute or more (>= 60 seconds)

---

## 📊 Schema Changes

### **core.videos Table - NEW COLUMNS**

```sql
CREATE TABLE core.videos (
    video_id VARCHAR(50) PRIMARY KEY,
    title TEXT NOT NULL,
    published_at TIMESTAMP NOT NULL,
    duration VARCHAR(50),              -- ISO 8601 format (PT22M26S)
    duration_readable VARCHAR(20),     -- Human readable (22:26)
    duration_seconds INTERVAL,         -- 🆕 INTERVAL type (00:22:26)
    duration_label VARCHAR(10),        -- 🆕 'short' or 'long'
    channel_id VARCHAR(50) NOT NULL,
    channel_handle VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**New Columns:**
| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `duration_seconds` | INTERVAL | Duration as PostgreSQL interval | `00:22:26` |
| `duration_label` | VARCHAR(10) | Video length category | `long` |

---

## 🔄 Transformation Logic

### **SQL Transformation (in transform_to_core function)**

```sql
WITH duration_calc AS (
    SELECT 
        video_id,
        -- Convert PT22M26S → total seconds
        COALESCE(
            EXTRACT(EPOCH FROM (
                regexp_replace(
                    regexp_replace(
                        regexp_replace(duration, 'PT', ''),
                        '(\d+)H', '\1 hours ')
                    , '(\d+)M', '\1 minutes ')
                , '(\d+)S', '\1 seconds'
            )::interval), 0
        ) AS total_seconds
    FROM staging.youtube_videos_raw
)
INSERT INTO core.videos (...)
SELECT 
    video_id,
    -- Convert seconds to INTERVAL
    (total_seconds || ' seconds')::INTERVAL AS duration_seconds,
    -- Label based on 60 second threshold
    CASE 
        WHEN total_seconds < 60 THEN 'short'
        ELSE 'long'
    END AS duration_label,
    ...
FROM duration_calc
```

### **Conversion Steps:**

1. **Remove 'PT' prefix:** `PT22M26S` → `22M26S`
2. **Replace H with 'hours':** `2H15M` → `2 hours 15M`
3. **Replace M with 'minutes':** `22M26S` → `22 minutes 26S`
4. **Replace S with 'seconds':** `26S` → `26 seconds`
5. **Cast to INTERVAL:** `22 minutes 26 seconds` → PostgreSQL INTERVAL
6. **Extract total seconds:** Calculate for comparison
7. **Create label:** `< 60` = 'short', `>= 60` = 'long'

---

## 📋 Example Data

### **Sample Videos with Labels:**

| video_id | title | duration | duration_readable | duration_seconds | duration_label |
|----------|-------|----------|-------------------|------------------|----------------|
| `SWc8fI_9iqA` | Ronaldo Teaches Me | PT15S | 0:15 | 00:00:15 | **short** |
| `CWbV3NItSdY` | World's Fastest Cleaners | PT35S | 0:35 | 00:00:35 | **short** |
| `ctJORnOjbrQ` | These Were The Good Days | PT52S | 0:52 | 00:00:52 | **short** |
| `erLbbextvlY` | 7 Days Stranded On An Island | PT22M26S | 22:26 | 00:22:26 | **long** |
| `l-nMKJ5J3Uc` | Ages 1-100 Decide Who Wins | PT40M2S | 40:02 | 00:40:02 | **long** |
| `ndAQfTzlVjc` | 7 Days Stranded In A Cave | PT17M59S | 17:59 | 00:17:59 | **long** |

### **Distribution Example (MrBeast channel):**

```sql
-- Count by duration label
SELECT duration_label, COUNT(*) as video_count
FROM core.videos
GROUP BY duration_label;
```

**Result:**
| duration_label | video_count |
|----------------|-------------|
| short | 45 videos |
| long | 859 videos |

---

## 🔍 Query Examples

### **1. Find all short videos (< 1 minute):**
```sql
SELECT video_id, title, duration_readable, duration_seconds
FROM core.videos
WHERE duration_label = 'short'
ORDER BY duration_seconds DESC;
```

### **2. Find videos by duration range:**
```sql
-- Videos between 10-20 minutes
SELECT video_id, title, duration_readable
FROM core.videos
WHERE duration_seconds >= INTERVAL '10 minutes'
  AND duration_seconds < INTERVAL '20 minutes';
```

### **3. Average duration by label:**
```sql
SELECT 
    duration_label,
    AVG(EXTRACT(EPOCH FROM duration_seconds)) as avg_seconds,
    COUNT(*) as video_count
FROM core.videos
GROUP BY duration_label;
```

**Result:**
| duration_label | avg_seconds | video_count |
|----------------|-------------|-------------|
| short | 32.5 | 45 |
| long | 892.3 | 859 |

### **4. Longest and shortest videos:**
```sql
-- Top 5 longest videos
SELECT title, duration_readable, duration_seconds
FROM core.videos
ORDER BY duration_seconds DESC
LIMIT 5;

-- Top 5 shortest videos
SELECT title, duration_readable, duration_seconds
FROM core.videos
ORDER BY duration_seconds ASC
LIMIT 5;
```

---

## 🎯 Use Cases

### **1. Content Analysis**
```sql
-- How many short vs long videos are there?
SELECT duration_label, COUNT(*) 
FROM core.videos 
GROUP BY duration_label;
```

### **2. Performance Analysis**
```sql
-- Do short videos get more views?
SELECT 
    v.duration_label,
    AVG(vs.view_count) as avg_views,
    AVG(vs.like_count) as avg_likes
FROM core.videos v
JOIN core.video_statistics vs ON v.video_id = vs.video_id
GROUP BY v.duration_label;
```

### **3. Duration-based Filtering**
```sql
-- Find popular short videos (YouTube Shorts candidates)
SELECT v.title, v.duration_readable, vs.view_count
FROM core.videos v
JOIN core.video_statistics vs ON v.video_id = vs.video_id
WHERE v.duration_label = 'short'
  AND vs.view_count > 1000000
ORDER BY vs.view_count DESC;
```

### **4. Time-series Analysis**
```sql
-- Track how video duration changes over time
SELECT 
    DATE_TRUNC('month', published_at) as month,
    duration_label,
    COUNT(*) as video_count,
    AVG(EXTRACT(EPOCH FROM duration_seconds)) as avg_duration
FROM core.videos
GROUP BY month, duration_label
ORDER BY month DESC;
```

---

## 🚀 Benefits

### **1. Better Analytics**
- ✅ Easy duration-based filtering
- ✅ Calculate average video lengths
- ✅ Compare short vs long video performance

### **2. Simplified Queries**
- ✅ No need to parse ISO 8601 in SQL
- ✅ Direct INTERVAL comparisons
- ✅ Simple label-based filtering

### **3. Business Insights**
- ✅ Identify content trends (short vs long)
- ✅ Optimize video length strategy
- ✅ Compare engagement by duration

---

## 🔧 Migration Required

### **For Existing Databases:**

If you already have data in `core.videos`, run this to add the new columns:

```sql
-- Add new columns
ALTER TABLE core.videos 
ADD COLUMN duration_seconds INTERVAL,
ADD COLUMN duration_label VARCHAR(10);

-- Populate with existing data
WITH duration_calc AS (
    SELECT 
        video_id,
        COALESCE(
            EXTRACT(EPOCH FROM (
                regexp_replace(
                    regexp_replace(
                        regexp_replace(duration, 'PT', ''),
                        '(\d+)H', '\1 hours ')
                    , '(\d+)M', '\1 minutes ')
                , '(\d+)S', '\1 seconds'
            )::interval), 0
        ) AS total_seconds
    FROM core.videos
)
UPDATE core.videos v
SET 
    duration_seconds = (dc.total_seconds || ' seconds')::INTERVAL,
    duration_label = CASE 
        WHEN dc.total_seconds < 60 THEN 'short'
        ELSE 'long'
    END
FROM duration_calc dc
WHERE v.video_id = dc.video_id;
```

### **For Fresh Setup:**

Just run the updated `create_schemas.sql` - the columns are already included!

---

## 📊 Data Quality Checks

Consider adding these Soda checks to `videos_quality.yml`:

```yaml
checks for core.videos:
  # Duration label validation
  - invalid_count(duration_label) = 0:
      valid values: ['short', 'long']
      
  # Duration consistency
  - failed rows:
      fail condition: |
        duration_label = 'short' AND 
        EXTRACT(EPOCH FROM duration_seconds) >= 60
        
  # No null durations
  - missing_count(duration_seconds) = 0
  - missing_count(duration_label) = 0
```

---

## ✅ Summary

**What Changed:**
- ✅ Added `duration_seconds` column (INTERVAL type)
- ✅ Added `duration_label` column ('short' or 'long')
- ✅ Updated `transform_to_core()` function
- ✅ Automatic calculation on every ETL run
- ✅ No manual intervention needed

**Threshold:**
- **Short videos:** < 60 seconds
- **Long videos:** >= 60 seconds

**Benefits:**
- 🚀 Easy analytics by video length
- 📊 Better business insights
- ⚡ Faster queries (no parsing needed)
- 🎯 Clear content categorization

🎉 **Your videos are now automatically categorized by duration!**
