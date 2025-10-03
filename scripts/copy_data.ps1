# ============================================
# 📦 YouTube ELT Pipeline - Copy Data Script
# ============================================
# Description: Copy files between Docker container and host
# Usage: .\scripts\copy_data.ps1 [to-container|from-container] [file/directory]

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("to-container", "from-container", "logs", "json", "reports")]
    [string]$Action = "help",
    
    [Parameter(Mandatory=$false)]
    [string]$Path = ""
)

# ============================================
# Configuration
# ============================================
$CONTAINER_NAME = "version-final_d97706-scheduler-1"  # Main Airflow container
$PROJECT_ROOT = Get-Location

# ============================================
# Helper Functions
# ============================================
function Show-Help {
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host "📦 YouTube ELT Pipeline - Copy Data" -ForegroundColor Cyan
    Write-Host "============================================`n" -ForegroundColor Cyan
    
    Write-Host "Usage:" -ForegroundColor Yellow
    Write-Host "  .\scripts\copy_data.ps1 [action] [path]`n" -ForegroundColor White
    
    Write-Host "Actions:" -ForegroundColor Yellow
    Write-Host "  logs           - Copy Airflow logs from container to host" -ForegroundColor White
    Write-Host "  json           - Copy JSON data files from container to host" -ForegroundColor White
    Write-Host "  reports        - Copy Soda quality reports from container to host" -ForegroundColor White
    Write-Host "  to-container   - Copy file/folder from host to container" -ForegroundColor White
    Write-Host "  from-container - Copy file/folder from container to host" -ForegroundColor White
    
    Write-Host "`nExamples:" -ForegroundColor Yellow
    Write-Host "  .\scripts\copy_data.ps1 logs" -ForegroundColor Cyan
    Write-Host "  .\scripts\copy_data.ps1 json" -ForegroundColor Cyan
    Write-Host "  .\scripts\copy_data.ps1 reports" -ForegroundColor Cyan
    Write-Host "  .\scripts\copy_data.ps1 to-container include/youtube_data/MrBeast.json" -ForegroundColor Cyan
    Write-Host "  .\scripts\copy_data.ps1 from-container /usr/local/airflow/logs" -ForegroundColor Cyan
    Write-Host "`n============================================`n" -ForegroundColor Cyan
}

function Check-Container {
    try {
        $containerStatus = docker ps --filter "name=$CONTAINER_NAME" --format "{{.Status}}"
        if (-Not $containerStatus) {
            Write-Host "❌ Container not running: $CONTAINER_NAME" -ForegroundColor Red
            Write-Host "   Start Airflow: astro dev start" -ForegroundColor Yellow
            exit 1
        }
        Write-Host "✅ Container running: $CONTAINER_NAME" -ForegroundColor Green
    } catch {
        Write-Host "❌ Docker not available or container not found" -ForegroundColor Red
        exit 1
    }
}

# ============================================
# Main Script
# ============================================
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "📦 Copy Data - YouTube ELT Pipeline" -ForegroundColor Cyan
Write-Host "============================================`n" -ForegroundColor Cyan

if ($Action -eq "help") {
    Show-Help
    exit 0
}

# Check container status
Check-Container

# ============================================
# Execute Action
# ============================================
switch ($Action) {
    "logs" {
        Write-Host "📋 Copying Airflow logs from container..." -ForegroundColor Yellow
        $destination = "logs_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
        
        docker cp "${CONTAINER_NAME}:/usr/local/airflow/logs" $destination
        
        if ($?) {
            Write-Host "✅ Logs copied to: $destination" -ForegroundColor Green
        } else {
            Write-Host "❌ Failed to copy logs" -ForegroundColor Red
            exit 1
        }
    }
    
    "json" {
        Write-Host "📄 Copying JSON data files from container..." -ForegroundColor Yellow
        $destination = "include/youtube_data"
        
        # Create destination if not exists
        if (-Not (Test-Path $destination)) {
            New-Item -ItemType Directory -Path $destination -Force | Out-Null
        }
        
        docker cp "${CONTAINER_NAME}:/usr/local/airflow/include/youtube_data/." $destination
        
        if ($?) {
            Write-Host "✅ JSON files copied to: $destination" -ForegroundColor Green
            Get-ChildItem $destination | Format-Table Name, Length, LastWriteTime
        } else {
            Write-Host "❌ Failed to copy JSON files" -ForegroundColor Red
            exit 1
        }
    }
    
    "reports" {
        Write-Host "📊 Copying Soda quality reports from container..." -ForegroundColor Yellow
        $destination = "include/soda/reports"
        
        # Create destination if not exists
        if (-Not (Test-Path $destination)) {
            New-Item -ItemType Directory -Path $destination -Force | Out-Null
        }
        
        docker cp "${CONTAINER_NAME}:/usr/local/airflow/include/soda/reports/." $destination
        
        if ($?) {
            Write-Host "✅ Reports copied to: $destination" -ForegroundColor Green
            Get-ChildItem $destination | Format-Table Name, Length, LastWriteTime
        } else {
            Write-Host "❌ Failed to copy reports" -ForegroundColor Red
            exit 1
        }
    }
    
    "to-container" {
        if (-Not $Path) {
            Write-Host "❌ Please specify a file or directory to copy" -ForegroundColor Red
            Write-Host "   Usage: .\scripts\copy_data.ps1 to-container <path>" -ForegroundColor Yellow
            exit 1
        }
        
        if (-Not (Test-Path $Path)) {
            Write-Host "❌ Path not found: $Path" -ForegroundColor Red
            exit 1
        }
        
        Write-Host "📤 Copying to container: $Path" -ForegroundColor Yellow
        docker cp $Path "${CONTAINER_NAME}:/usr/local/airflow/$Path"
        
        if ($?) {
            Write-Host "✅ Copied successfully to container" -ForegroundColor Green
        } else {
            Write-Host "❌ Failed to copy to container" -ForegroundColor Red
            exit 1
        }
    }
    
    "from-container" {
        if (-Not $Path) {
            Write-Host "❌ Please specify a container path to copy" -ForegroundColor Red
            Write-Host "   Usage: .\scripts\copy_data.ps1 from-container <container-path>" -ForegroundColor Yellow
            exit 1
        }
        
        $destination = "copied_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
        Write-Host "📥 Copying from container: $Path" -ForegroundColor Yellow
        
        docker cp "${CONTAINER_NAME}:$Path" $destination
        
        if ($?) {
            Write-Host "✅ Copied to: $destination" -ForegroundColor Green
        } else {
            Write-Host "❌ Failed to copy from container" -ForegroundColor Red
            exit 1
        }
    }
}

Write-Host "`n============================================`n" -ForegroundColor Cyan
