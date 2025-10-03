-- Update duration_seconds and duration_label for existing videos
DO $$
DECLARE
    video_rec RECORD;
    hours INT;
    minutes INT;
    seconds INT;
    total_secs INT;
BEGIN
    FOR video_rec IN SELECT video_id, duration FROM core.videos WHERE duration_seconds IS NULL LOOP
        -- Extract hours, minutes, seconds from PT format
        hours := COALESCE((regexp_matches(video_rec.duration, '(\d+)H'))[1]::int, 0);
        minutes := COALESCE((regexp_matches(video_rec.duration, '(\d+)M'))[1]::int, 0);
        seconds := COALESCE((regexp_matches(video_rec.duration, '(\d+)S'))[1]::int, 0);
        
        -- Calculate total seconds
        total_secs := (hours * 3600) + (minutes * 60) + seconds;
        
        -- Update the record
        UPDATE core.videos
        SET 
            duration_seconds = make_interval(secs => total_secs),
            duration_label = CASE WHEN total_secs < 60 THEN 'short' ELSE 'long' END
        WHERE video_id = video_rec.video_id;
    END LOOP;
    
    RAISE NOTICE 'Updated % videos', (SELECT COUNT(*) FROM core.videos WHERE duration_label IS NOT NULL);
END $$;

-- Show results
SELECT duration_label, COUNT(*) as count 
FROM core.videos 
GROUP BY duration_label 
ORDER BY duration_label;
