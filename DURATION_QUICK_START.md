# ✅ Duration Transformation - Quick Start Guide

## 🎯 What Was Changed

You now have **automatic duration analysis** in your pipeline!

### **New Features:**
1. **duration_seconds** - Duration as PostgreSQL INTERVAL for easy calculations
2. **duration_label** - Automatic categorization: 
   - 🔴 **"short"** = Videos < 1 minute (< 60 seconds)
   - 🟢 **"long"** = Videos ≥ 1 minute (≥ 60 seconds)

---

## 📝 Files Modified

### **1. Schema File** ✅
**File:** `include/sql/create_schemas.sql`

**Added columns to `core.videos`:**
```sql
duration_seconds INTERVAL,      -- e.g., 00:22:26
duration_label VARCHAR(10),     -- 'short' or 'long'
```

### **2. ETL DAG** ✅
**File:** `dags/youtube_load_db.py`

**Updated `transform_to_core()` function:**
- Converts ISO 8601 duration (PT22M26S) to INTERVAL
- Calculates duration label based on 60-second threshold
- Uses WITH clause for cleaner SQL

---

## 🚀 How to Apply Changes

### **Option 1: Fresh Database (Recommended)**

If you haven't loaded important data yet:

```bash
# In Airflow UI or terminal
1. Delete existing database (if any)
2. Run create_schemas.sql to recreate tables
3. Run your produce_JSON → update_db pipeline
4. New columns will be populated automatically!
```

### **Option 2: Migrate Existing Database**

If you already have data in `core.videos`:

```sql
-- Connect to postgres_dwh database

-- Step 1: Add new columns
ALTER TABLE core.videos 
ADD COLUMN duration_seconds INTERVAL,
ADD COLUMN duration_label VARCHAR(10);

-- Step 2: Populate existing data
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

-- Step 3: Verify
SELECT duration_label, COUNT(*) 
FROM core.videos 
GROUP BY duration_label;
```

---

## 🧪 Test It Out

### **1. Run Your Pipeline**

In Airflow UI:
1. Trigger `produce_JSON` DAG (or run manually)
2. Wait for `update_db` to complete
3. Check `core.videos` table

### **2. Query the Results**

```sql
-- See short videos
SELECT video_id, title, duration_readable, duration_label
FROM core.videos
WHERE duration_label = 'short'
ORDER BY duration_seconds
LIMIT 10;

-- See long videos  
SELECT video_id, title, duration_readable, duration_label
FROM core.videos
WHERE duration_label = 'long'
ORDER BY duration_seconds DESC
LIMIT 10;

-- Count by category
SELECT duration_label, COUNT(*) as count
FROM core.videos
GROUP BY duration_label;
```

### **Expected Results (MrBeast example):**

```
duration_label | count
---------------|-------
short          | 45
long           | 859
```

---

## 📊 Sample Data

### **Short Videos (< 1 minute):**
| Title | Duration | duration_seconds | Label |
|-------|----------|------------------|-------|
| Ronaldo Teaches Me To SIUU | 0:15 | 00:00:15 | short |
| World's Fastest Cleaners | 0:35 | 00:00:35 | short |
| These Were The Good Days | 0:52 | 00:00:52 | short |

### **Long Videos (≥ 1 minute):**
| Title | Duration | duration_seconds | Label |
|-------|----------|------------------|-------|
| 7 Days Stranded On An Island | 22:26 | 00:22:26 | long |
| Ages 1-100 Decide Who Wins | 40:02 | 00:40:02 | long |
| 7 Days Stranded In A Cave | 17:59 | 00:17:59 | long |

---

## 🎯 Use Cases

### **Analytics Queries:**

```sql
-- Average views by duration type
SELECT 
    v.duration_label,
    AVG(s.view_count) as avg_views,
    COUNT(*) as video_count
FROM core.videos v
JOIN core.video_statistics s ON v.video_id = s.video_id
GROUP BY v.duration_label;

-- Find viral short videos
SELECT v.title, v.duration_readable, s.view_count
FROM core.videos v
JOIN core.video_statistics s ON v.video_id = s.video_id
WHERE v.duration_label = 'short'
  AND s.view_count > 100000000  -- 100M+ views
ORDER BY s.view_count DESC;

-- Duration trend over time
SELECT 
    DATE_TRUNC('year', published_at) as year,
    duration_label,
    COUNT(*) as count
FROM core.videos
GROUP BY year, duration_label
ORDER BY year DESC, duration_label;
```

---

## ✅ Verification Checklist

After applying changes:

- [ ] Schema updated with new columns
- [ ] DAG code updated with transformation logic
- [ ] Pipeline runs without errors
- [ ] `duration_seconds` column populated
- [ ] `duration_label` shows 'short' or 'long'
- [ ] Short videos have `< 60 seconds`
- [ ] Long videos have `>= 60 seconds`
- [ ] Test queries return expected results

---

## 🆘 Troubleshooting

### **Error: Column doesn't exist**
```
ERROR: column "duration_seconds" does not exist
```

**Solution:** Run the ALTER TABLE commands to add the columns (see Option 2 above).

### **Error: Invalid regex**
```
ERROR: invalid regular expression
```

**Solution:** Make sure you're using `\\d+` (double backslash) in the Python string.

### **All videos showing as 'long'**
```
Check the duration values in staging table
```

**Solution:** Verify ISO 8601 format is correct (PT22M26S format).

---

## 📚 Documentation

**Full details:** See `DURATION_TRANSFORMATION.md`

**Includes:**
- Complete SQL transformation logic
- Example queries for analytics
- Performance analysis use cases
- Data quality check suggestions
- Migration scripts

---

## 🎉 Benefits

✅ **Automatic categorization** - No manual work needed  
✅ **Easy analytics** - Simple queries with labels  
✅ **Better insights** - Compare short vs long video performance  
✅ **Future-proof** - INTERVAL type allows complex calculations  
✅ **Production-ready** - Runs on every ETL execution  

**Your pipeline now automatically analyzes video durations!** 🚀

---

## 📞 Next Steps

1. ✅ Apply schema changes (fresh DB or migration)
2. ✅ Run your pipeline (produce_JSON → update_db)
3. ✅ Query `core.videos` to see the labels
4. ✅ Build analytics dashboards using duration_label
5. ✅ Enjoy automatic video categorization!

**Happy analyzing!** 📊
