# Quick Fix Script for UNIQUE Constraint Issue
# Run this from: C:\Users\user\Desktop\version-final

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  FIXING UNIQUE CONSTRAINT ON video_id  " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Choose your fix method:" -ForegroundColor Yellow
Write-Host "1. Fresh Start (Delete all data, recreate database)" -ForegroundColor White
Write-Host "2. Add Constraint (Keep existing data)" -ForegroundColor White
Write-Host "3. Manual (I'll do it myself)" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Enter choice (1, 2, or 3)"

if ($choice -eq "1") {
    Write-Host ""
    Write-Host "Option 1: Fresh Start" -ForegroundColor Green
    Write-Host "This will DELETE all data and recreate the database." -ForegroundColor Red
    Write-Host ""
    $confirm = Read-Host "Are you sure? Type 'YES' to continue"
    
    if ($confirm -eq "YES") {
        Write-Host ""
        Write-Host "Stopping Airflow..." -ForegroundColor Yellow
        astro dev stop
        
        Write-Host ""
        Write-Host "Removing database volume..." -ForegroundColor Yellow
        docker volume rm version-final_postgres-db-volume
        
        Write-Host ""
        Write-Host "Starting Airflow (will recreate database with fix)..." -ForegroundColor Yellow
        astro dev start
        
        Write-Host ""
        Write-Host "✅ Done! Database recreated with UNIQUE constraint." -ForegroundColor Green
        Write-Host "Wait for Airflow to start, then run your DAG." -ForegroundColor Cyan
    } else {
        Write-Host "Cancelled." -ForegroundColor Red
    }
}
elseif ($choice -eq "2") {
    Write-Host ""
    Write-Host "Option 2: Add Constraint to Existing Table" -ForegroundColor Green
    Write-Host ""
    Write-Host "Run these commands in PostgreSQL:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "-- Enter scheduler container" -ForegroundColor Gray
    Write-Host "docker exec -it version-final-scheduler-1 bash" -ForegroundColor White
    Write-Host ""
    Write-Host "-- Connect to database" -ForegroundColor Gray
    Write-Host "psql postgresql://postgres:postgres@postgres:5432/youtube_dwh" -ForegroundColor White
    Write-Host ""
    Write-Host "-- Add UNIQUE constraint" -ForegroundColor Gray
    Write-Host "ALTER TABLE staging.youtube_videos_raw ADD CONSTRAINT video_id_unique UNIQUE (video_id);" -ForegroundColor White
    Write-Host ""
    Write-Host "-- Exit" -ForegroundColor Gray
    Write-Host "\q" -ForegroundColor White
    Write-Host "exit" -ForegroundColor White
    Write-Host ""
    Write-Host "See FIX_UNIQUE_CONSTRAINT.md for complete migration script." -ForegroundColor Yellow
}
else {
    Write-Host ""
    Write-Host "Manual Fix Selected" -ForegroundColor Green
    Write-Host ""
    Write-Host "The schema file has been updated:" -ForegroundColor Cyan
    Write-Host "  include/sql/create_schemas.sql" -ForegroundColor White
    Write-Host ""
    Write-Host "Complete instructions in:" -ForegroundColor Cyan
    Write-Host "  FIX_UNIQUE_CONSTRAINT.md" -ForegroundColor White
    Write-Host ""
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "For detailed instructions, see:" -ForegroundColor Yellow
Write-Host "  FIX_UNIQUE_CONSTRAINT.md" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
