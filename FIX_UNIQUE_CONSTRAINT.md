# 🔧 URGENT FIX: Missing UNIQUE Constraint on video_id

## ❌ Error Found

```
InvalidColumnReference: there is no unique or exclusion constraint matching the ON CONFLICT specification
```

## 🎯 Root Cause

The `staging.youtube_videos_raw` table has `video_id` as a regular column with an INDEX, but **NOT a UNIQUE constraint**. The `ON CONFLICT (video_id)` clause in the UPSERT query requires either:
- UNIQUE constraint
- PRIMARY KEY

## ✅ Fix Applied

### **Schema File Updated:**
`include/sql/create_schemas.sql`

**Changed:**
```sql
video_id VARCHAR(50) NOT NULL,  ❌ No UNIQUE constraint
```

**To:**
```sql
video_id VARCHAR(50) NOT NULL UNIQUE,  ✅ UNIQUE constraint added
```

---

## 🚀 How to Apply the Fix

### **Option 1: Fresh Database (Recommended)**

If your database is empty or you can drop it:

```sql
-- 1. Drop existing tables
DROP SCHEMA IF EXISTS staging CASCADE;
DROP SCHEMA IF EXISTS core CASCADE;

-- 2. Reconnect to Airflow UI and run the DAG
-- The create_schemas.sql will automatically run with the fix
```

### **Option 2: Add UNIQUE Constraint to Existing Table**

If you have data you want to keep:

```sql
-- Connect to postgres_dwh database

-- Step 1: Remove duplicates (if any)
DELETE FROM staging.youtube_videos_raw a
USING staging.youtube_videos_raw b
WHERE a.id > b.id
  AND a.video_id = b.video_id;

-- Step 2: Add UNIQUE constraint
ALTER TABLE staging.youtube_videos_raw
ADD CONSTRAINT video_id_unique UNIQUE (video_id);

-- Step 3: Verify
SELECT 
    constraint_name, 
    constraint_type 
FROM information_schema.table_constraints 
WHERE table_name = 'youtube_videos_raw' 
  AND table_schema = 'staging';
```

**Expected Result:**
```
constraint_name              | constraint_type
-----------------------------|----------------
youtube_videos_raw_pkey      | PRIMARY KEY
video_id_unique              | UNIQUE
```

---

## 📋 Complete Migration Script

Run this in your PostgreSQL database:

```sql
-- ================================================
-- Migration: Add UNIQUE constraint to video_id
-- ================================================

-- Step 1: Check for duplicates
SELECT video_id, COUNT(*) as count
FROM staging.youtube_videos_raw
GROUP BY video_id
HAVING COUNT(*) > 1;

-- Step 2: Remove duplicates (keep the first one)
WITH duplicates AS (
    SELECT id,
           ROW_NUMBER() OVER (PARTITION BY video_id ORDER BY id) as rn
    FROM staging.youtube_videos_raw
)
DELETE FROM staging.youtube_videos_raw
WHERE id IN (
    SELECT id FROM duplicates WHERE rn > 1
);

-- Step 3: Add UNIQUE constraint
ALTER TABLE staging.youtube_videos_raw
ADD CONSTRAINT video_id_unique UNIQUE (video_id);

-- Step 4: Verify constraint was added
\d staging.youtube_videos_raw

-- Step 5: Test UPSERT query
-- This should now work without error
INSERT INTO staging.youtube_videos_raw (
    video_id, title, published_at, duration, duration_readable,
    view_count, like_count, comment_count,
    channel_id, channel_handle, extraction_date
) VALUES (
    'TEST123', 'Test Video', NOW(), 'PT5M30S', '5:30',
    1000, 100, 10,
    'TESTCHANNEL', '@testhandle', NOW()
)
ON CONFLICT (video_id) DO UPDATE SET
    title = EXCLUDED.title,
    view_count = EXCLUDED.view_count;

-- Cleanup test data
DELETE FROM staging.youtube_videos_raw WHERE video_id = 'TEST123';
```

---

## 🔍 How to Apply Using Docker

### **Method 1: Via Airflow Scheduler Container**

```bash
# Enter the scheduler container
docker exec -it version-final-scheduler-1 bash

# Connect to PostgreSQL
psql postgresql://postgres:postgres@postgres:5432/youtube_dwh

# Run the migration SQL above
# Then exit
\q
exit
```

### **Method 2: Via PostgreSQL Container**

```bash
# Enter the postgres container
docker exec -it version-final-postgres-1 bash

# Connect to database
psql -U postgres -d youtube_dwh

# Run the migration SQL above
# Then exit
\q
exit
```

### **Method 3: Fresh Start (Easiest)**

```powershell
# Stop Airflow
cd C:\Users\user\Desktop\version-final
astro dev stop

# Remove volumes (deletes all data)
docker volume rm version-final_postgres-db-volume

# Start Airflow (will recreate database with fix)
astro dev start
```

---

## ✅ Verification Steps

After applying the fix:

### **1. Check Constraint Exists**

```sql
SELECT 
    tc.constraint_name,
    tc.constraint_type,
    kcu.column_name
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu
  ON tc.constraint_name = kcu.constraint_name
WHERE tc.table_schema = 'staging'
  AND tc.table_name = 'youtube_videos_raw'
  AND kcu.column_name = 'video_id';
```

**Expected Output:**
```
constraint_name  | constraint_type | column_name
-----------------|-----------------|------------
video_id_unique  | UNIQUE          | video_id
```

### **2. Run the DAG**

In Airflow UI:
1. Go to DAGs
2. Find `update_db`
3. Trigger manually
4. Check logs - should show no errors

### **3. Verify Data Loaded**

```sql
-- Count videos in staging
SELECT COUNT(*) FROM staging.youtube_videos_raw;

-- Check for duplicates (should be 0)
SELECT video_id, COUNT(*) 
FROM staging.youtube_videos_raw 
GROUP BY video_id 
HAVING COUNT(*) > 1;

-- Show sample data
SELECT video_id, title, view_count 
FROM staging.youtube_videos_raw 
LIMIT 5;
```

---

## 📊 What Changed

### **Before (BROKEN):**
```sql
CREATE TABLE staging.youtube_videos_raw (
    id SERIAL PRIMARY KEY,
    video_id VARCHAR(50) NOT NULL,  ❌ No UNIQUE
    ...
);
```

**Problem:** `ON CONFLICT (video_id)` fails because no UNIQUE constraint

### **After (FIXED):**
```sql
CREATE TABLE staging.youtube_videos_raw (
    id SERIAL PRIMARY KEY,
    video_id VARCHAR(50) NOT NULL UNIQUE,  ✅ UNIQUE constraint
    ...
);
```

**Result:** `ON CONFLICT (video_id)` works perfectly for UPSERT

---

## 🎯 Why This Matters

### **UPSERT Logic Requires UNIQUE Constraint:**

```sql
INSERT INTO staging.youtube_videos_raw (...)
VALUES (...)
ON CONFLICT (video_id) DO UPDATE SET ...
          ↑
          This requires video_id to have UNIQUE constraint
```

**PostgreSQL Rules:**
- `ON CONFLICT` requires a **unique index** or **unique constraint**
- Regular INDEX is NOT enough
- UNIQUE constraint creates an underlying unique index automatically

---

## 🔄 Impact on Pipeline

### **Before Fix:**
```
produce_JSON ✅ → update_db ❌ (fails at sync_to_staging)
                     ↓
              "no unique constraint" error
```

### **After Fix:**
```
produce_JSON ✅ → update_db ✅ → data_quality ✅
                     ↓
              UPSERT works perfectly
```

---

## 📝 Summary

**Issue:** Missing UNIQUE constraint on `staging.youtube_videos_raw.video_id`  
**Impact:** UPSERT (ON CONFLICT) fails  
**Fix:** Added `UNIQUE` constraint to `video_id` column  
**Status:** ✅ Schema updated, migration script provided  

**Next Steps:**
1. Choose migration method (fresh DB or add constraint)
2. Apply the fix
3. Run `update_db` DAG
4. Verify data loads successfully

---

## 🆘 Troubleshooting

### **Error: "constraint already exists"**
```
Already have the fix! No action needed.
```

### **Error: "duplicate key value violates unique constraint"**
```sql
-- Find and remove duplicates first
DELETE FROM staging.youtube_videos_raw a
USING staging.youtube_videos_raw b
WHERE a.id > b.id AND a.video_id = b.video_id;
```

### **Error: "relation does not exist"**
```sql
-- Recreate the schema
DROP SCHEMA IF EXISTS staging CASCADE;
DROP SCHEMA IF EXISTS core CASCADE;

-- Then run create_schemas.sql
```

---

## ✅ Files Updated

1. ✅ `include/sql/create_schemas.sql` - Added UNIQUE constraint
2. ✅ This migration guide created

**Your pipeline will work after applying this fix!** 🚀
