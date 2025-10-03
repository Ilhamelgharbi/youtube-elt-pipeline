# ============================================
# 🚀 YouTube ELT Pipeline - Deploy Script
# ============================================
# Description: Deploy pipeline to production or restart services
# Usage: .\scripts\deploy.ps1 [local|restart|stop|status]

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("local", "restart", "stop", "status", "build")]
    [string]$Action = "local"
)

# ============================================
# Configuration
# ============================================
$PROJECT_NAME = "YouTube ELT Pipeline"

# ============================================
# Helper Functions
# ============================================
function Show-Header {
    param([string]$Title)
    Write-Host "`n============================================" -ForegroundColor Cyan
    Write-Host "🚀 $Title" -ForegroundColor Cyan
    Write-Host "============================================`n" -ForegroundColor Cyan
}

function Check-Prerequisites {
    Write-Host "📋 Checking prerequisites..." -ForegroundColor Yellow
    
    # Check Docker
    try {
        docker --version | Out-Null
        Write-Host "✅ Docker is running" -ForegroundColor Green
    } catch {
        Write-Host "❌ Docker not found or not running" -ForegroundColor Red
        Write-Host "   Please start Docker Desktop" -ForegroundColor Yellow
        exit 1
    }
    
    # Check Astro CLI
    try {
        astro version | Out-Null
        Write-Host "✅ Astro CLI is available" -ForegroundColor Green
    } catch {
        Write-Host "❌ Astro CLI not found" -ForegroundColor Red
        Write-Host "   Install: winget install -e --id Astronomer.Astro" -ForegroundColor Yellow
        exit 1
    }
}

function Show-Status {
    Show-Header "Current Status"
    
    Write-Host "📊 Container Status:" -ForegroundColor Yellow
    astro dev ps
    
    Write-Host "`n🌐 Access Points:" -ForegroundColor Yellow
    Write-Host "   Airflow UI:  http://localhost:8080 (admin/admin)" -ForegroundColor Cyan
    Write-Host "   PostgreSQL:  localhost:5432" -ForegroundColor Cyan
    
    Write-Host "`n📂 Data Directories:" -ForegroundColor Yellow
    if (Test-Path "include/youtube_data") {
        $jsonCount = (Get-ChildItem "include/youtube_data" -Filter "*.json" | Measure-Object).Count
        Write-Host "   JSON files:  $jsonCount files" -ForegroundColor Cyan
    }
    if (Test-Path "include/soda/reports") {
        $reportCount = (Get-ChildItem "include/soda/reports" -Filter "*.json" | Measure-Object).Count
        Write-Host "   Reports:     $reportCount reports" -ForegroundColor Cyan
    }
}

# ============================================
# Main Deployment Logic
# ============================================
Show-Header "$PROJECT_NAME - Deploy"

switch ($Action) {
    "local" {
        Write-Host "🚀 Deploying locally with Astro CLI...`n" -ForegroundColor Yellow
        
        Check-Prerequisites
        
        # Check if already running
        try {
            $running = astro dev ps 2>&1
            if ($running -match "running") {
                Write-Host "⚠️  Airflow is already running" -ForegroundColor Yellow
                Write-Host "   Use '.\scripts\deploy.ps1 restart' to restart`n" -ForegroundColor Cyan
                Show-Status
                exit 0
            }
        } catch {}
        
        # Start Airflow
        Write-Host "🔨 Building Docker images..." -ForegroundColor Yellow
        Write-Host "   This may take a few minutes...`n" -ForegroundColor Cyan
        
        astro dev start
        
        if ($?) {
            Write-Host "`n✅ Deployment successful!" -ForegroundColor Green
            Show-Status
        } else {
            Write-Host "`n❌ Deployment failed" -ForegroundColor Red
            exit 1
        }
    }
    
    "build" {
        Write-Host "🔨 Rebuilding Docker images...`n" -ForegroundColor Yellow
        
        Check-Prerequisites
        
        # Stop current containers
        Write-Host "⏸️  Stopping current containers..." -ForegroundColor Yellow
        astro dev stop
        
        # Start with fresh build
        Write-Host "`n🔨 Building fresh images..." -ForegroundColor Yellow
        astro dev start
        
        if ($?) {
            Write-Host "`n✅ Rebuild successful!" -ForegroundColor Green
            Show-Status
        } else {
            Write-Host "`n❌ Rebuild failed" -ForegroundColor Red
            exit 1
        }
    }
    
    "restart" {
        Write-Host "🔄 Restarting Airflow services...`n" -ForegroundColor Yellow
        
        Check-Prerequisites
        
        # Restart
        Write-Host "⏸️  Stopping containers..." -ForegroundColor Yellow
        astro dev stop
        
        Write-Host "`n▶️  Starting containers..." -ForegroundColor Yellow
        astro dev start
        
        if ($?) {
            Write-Host "`n✅ Restart successful!" -ForegroundColor Green
            Show-Status
        } else {
            Write-Host "`n❌ Restart failed" -ForegroundColor Red
            exit 1
        }
    }
    
    "stop" {
        Write-Host "⏹️  Stopping Airflow services...`n" -ForegroundColor Yellow
        
        astro dev stop
        
        if ($?) {
            Write-Host "`n✅ Stopped successfully!" -ForegroundColor Green
            Write-Host "`nTo restart: .\scripts\deploy.ps1 local`n" -ForegroundColor Cyan
        } else {
            Write-Host "`n❌ Failed to stop" -ForegroundColor Red
            exit 1
        }
    }
    
    "status" {
        Show-Status
    }
}

# ============================================
# Final Instructions
# ============================================
if ($Action -eq "local" -or $Action -eq "restart" -or $Action -eq "build") {
    Write-Host "`n============================================" -ForegroundColor Cyan
    Write-Host "📝 Next Steps:" -ForegroundColor Yellow
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host "1. Open Airflow UI: http://localhost:8080" -ForegroundColor White
    Write-Host "2. Login: admin / admin" -ForegroundColor White
    Write-Host "3. Enable DAGs:" -ForegroundColor White
    Write-Host "   - produce_JSON (Extract YouTube data)" -ForegroundColor Cyan
    Write-Host "   - update_db (Load to PostgreSQL)" -ForegroundColor Cyan
    Write-Host "   - data_quality (Soda validation)" -ForegroundColor Cyan
    Write-Host "4. Trigger produce_JSON DAG to start pipeline" -ForegroundColor White
    Write-Host "`nMonitor logs:" -ForegroundColor Yellow
    Write-Host "   astro dev logs" -ForegroundColor Cyan
    Write-Host "`n============================================`n" -ForegroundColor Cyan
}
