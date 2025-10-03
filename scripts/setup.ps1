# ============================================
# 🚀 YouTube ELT Pipeline - Setup Script
# ============================================
# Description: Initial project setup automation
# Usage: .\scripts\setup.ps1

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "🚀 YouTube ELT Pipeline - Setup" -ForegroundColor Cyan
Write-Host "============================================`n" -ForegroundColor Cyan

# ============================================
# 1. Check Prerequisites
# ============================================
Write-Host "📋 Checking prerequisites..." -ForegroundColor Yellow

# Check Docker
try {
    $dockerVersion = docker --version
    Write-Host "✅ Docker installed: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker not found. Please install Docker Desktop." -ForegroundColor Red
    exit 1
}

# Check Astro CLI
try {
    $astroVersion = astro version
    Write-Host "✅ Astro CLI installed: $astroVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Astro CLI not found. Install with: winget install -e --id Astronomer.Astro" -ForegroundColor Red
    exit 1
}

# Check Python
try {
    $pythonVersion = python --version
    Write-Host "✅ Python installed: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Python not found. Required for local testing." -ForegroundColor Yellow
}

# ============================================
# 2. Create Environment File
# ============================================
Write-Host "`n📝 Setting up environment variables..." -ForegroundColor Yellow

if (-Not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "✅ Created .env file from .env.example" -ForegroundColor Green
        Write-Host "⚠️  Please edit .env with your credentials:" -ForegroundColor Yellow
        Write-Host "   - YOUTUBE_API_KEY" -ForegroundColor Yellow
        Write-Host "   - POSTGRES credentials" -ForegroundColor Yellow
    } else {
        Write-Host "⚠️  .env.example not found. Please create .env manually." -ForegroundColor Yellow
    }
} else {
    Write-Host "✅ .env file already exists" -ForegroundColor Green
}

# ============================================
# 3. Create Required Directories
# ============================================
Write-Host "`n📂 Creating required directories..." -ForegroundColor Yellow

$directories = @(
    "include/youtube_data",
    "include/soda/reports",
    "logs"
)

foreach ($dir in $directories) {
    if (-Not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "✅ Created: $dir" -ForegroundColor Green
    } else {
        Write-Host "✅ Exists: $dir" -ForegroundColor Green
    }
}

# ============================================
# 4. Install Python Dependencies (Local)
# ============================================
Write-Host "`n📦 Installing Python dependencies..." -ForegroundColor Yellow

if (Test-Path "requirements.txt") {
    try {
        pip install -r requirements.txt --quiet
        Write-Host "✅ Python dependencies installed" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  Failed to install dependencies. Run manually: pip install -r requirements.txt" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️  requirements.txt not found" -ForegroundColor Yellow
}

# ============================================
# 5. Start Airflow with Astro
# ============================================
Write-Host "`n🚀 Starting Airflow with Astro CLI..." -ForegroundColor Yellow
Write-Host "   This will build Docker images and start containers..." -ForegroundColor Cyan

try {
    astro dev start
    Write-Host "`n✅ Airflow started successfully!" -ForegroundColor Green
    Write-Host "`n🌐 Access Airflow UI: http://localhost:8080" -ForegroundColor Cyan
    Write-Host "   Username: admin" -ForegroundColor Cyan
    Write-Host "   Password: admin" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Failed to start Airflow. Check Docker is running." -ForegroundColor Red
    exit 1
}

# ============================================
# 6. Summary
# ============================================
Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "✅ Setup Complete!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "1. Edit .env with your API keys" -ForegroundColor White
Write-Host "2. Open http://localhost:8080 (admin/admin)" -ForegroundColor White
Write-Host "3. Enable DAGs: produce_JSON, update_db, data_quality" -ForegroundColor White
Write-Host "4. Run tests: .\scripts\test.ps1" -ForegroundColor White
Write-Host "`n============================================`n" -ForegroundColor Cyan
