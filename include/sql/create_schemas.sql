-- ==========================================
-- 📋 YouTube Data Warehouse - Schema Creation
-- ==========================================
-- This script creates the staging and core schemas
-- for the YouTube ELT pipeline
-- ==========================================

-- Create schemas
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS core;

-- ==========================================
-- 🗂️ STAGING SCHEMA - Raw Data
-- ==========================================
-- This table stores raw data directly from JSON files
-- No transformations, just as extracted from YouTube API

CREATE TABLE IF NOT EXISTS staging.youtube_videos_raw (
    id SERIAL PRIMARY KEY,
    video_id VARCHAR(50) NOT NULL UNIQUE,  -- UNIQUE constraint for UPSERT
    title TEXT,
    published_at TIMESTAMP,
    duration VARCHAR(50),  -- ISO 8601 format (e.g., PT37M4S)
    duration_readable VARCHAR(20),  -- Human readable (e.g., 37:04)
    view_count BIGINT,
    like_count BIGINT,
    comment_count BIGINT,
    channel_id VARCHAR(50),
    channel_handle VARCHAR(100),
    extraction_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for faster queries on staging
CREATE INDEX IF NOT EXISTS idx_staging_video_id ON staging.youtube_videos_raw(video_id);
CREATE INDEX IF NOT EXISTS idx_staging_extraction ON staging.youtube_videos_raw(extraction_date);

-- ==========================================
-- 🏢 CORE SCHEMA - Transformed & Clean Data
-- ==========================================

-- Table 1: Videos (Dimension Table)
-- Stores video metadata (slowly changing dimension)
CREATE TABLE IF NOT EXISTS core.videos (
    video_id VARCHAR(50) PRIMARY KEY,
    title TEXT NOT NULL,
    published_at TIMESTAMP NOT NULL,
    duration VARCHAR(50),  -- ISO 8601 format
    duration_readable VARCHAR(20),  -- Human readable
    duration_seconds INTERVAL,  -- Duration as interval (for calculations)
    duration_label VARCHAR(10),  -- 'short' (<1 min) or 'long' (>=1 min)
    channel_id VARCHAR(50) NOT NULL,
    channel_handle VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table 2: Video Statistics (Fact Table)
-- Stores time-series statistics for each video
-- This allows tracking how views/likes/comments change over time
CREATE TABLE IF NOT EXISTS core.video_statistics (
    id SERIAL PRIMARY KEY,
    video_id VARCHAR(50) NOT NULL,
    view_count BIGINT DEFAULT 0,
    like_count BIGINT DEFAULT 0,
    comment_count BIGINT DEFAULT 0,
    recorded_at TIMESTAMP NOT NULL,  -- When these stats were recorded
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraint
    CONSTRAINT fk_video 
        FOREIGN KEY (video_id) 
        REFERENCES core.videos(video_id) 
        ON DELETE CASCADE
);

-- ==========================================
-- 📊 INDEXES for Performance
-- ==========================================

-- Indexes on core.videos
CREATE INDEX IF NOT EXISTS idx_videos_channel ON core.videos(channel_id);
CREATE INDEX IF NOT EXISTS idx_videos_published ON core.videos(published_at);

-- Indexes on core.video_statistics
CREATE INDEX IF NOT EXISTS idx_stats_video ON core.video_statistics(video_id);
CREATE INDEX IF NOT EXISTS idx_stats_recorded ON core.video_statistics(recorded_at);
CREATE INDEX IF NOT EXISTS idx_stats_video_recorded ON core.video_statistics(video_id, recorded_at);

-- ==========================================
-- 📝 VIEWS for Easy Querying
-- ==========================================

-- View: Latest statistics for each video
CREATE OR REPLACE VIEW core.videos_latest_stats AS
SELECT 
    v.video_id,
    v.title,
    v.published_at,
    v.duration_readable,
    vs.view_count,
    vs.like_count,
    vs.comment_count,
    vs.recorded_at as stats_date
FROM core.videos v
JOIN LATERAL (
    SELECT view_count, like_count, comment_count, recorded_at
    FROM core.video_statistics
    WHERE video_id = v.video_id
    ORDER BY recorded_at DESC
    LIMIT 1
) vs ON true;

-- View: Video statistics history (all records)
CREATE OR REPLACE VIEW core.video_stats_history AS
SELECT 
    v.video_id,
    v.title,
    v.channel_handle,
    vs.view_count,
    vs.like_count,
    vs.comment_count,
    vs.recorded_at,
    v.published_at
FROM core.videos v
JOIN core.video_statistics vs ON v.video_id = vs.video_id
ORDER BY vs.recorded_at DESC;

-- ==========================================
-- ✅ SUCCESS MESSAGE
-- ==========================================

DO $$
BEGIN
    RAISE NOTICE '✅ Schemas created successfully!';
    RAISE NOTICE '📊 Staging schema: staging.youtube_videos_raw';
    RAISE NOTICE '🏢 Core schema: core.videos + core.video_statistics';
    RAISE NOTICE '📈 Views: core.videos_latest_stats + core.video_stats_history';
END $$;
