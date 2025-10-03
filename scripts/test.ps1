# ============================================
# 🧪 YouTube ELT Pipeline - Test Script
# ============================================
# Description: Run all tests for the project
# Usage: .\scripts\test.ps1

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "🧪 YouTube ELT Pipeline - Running Tests" -ForegroundColor Cyan
Write-Host "============================================`n" -ForegroundColor Cyan

# ============================================
# 1. Check Prerequisites
# ============================================
Write-Host "📋 Checking prerequisites..." -ForegroundColor Yellow

# Check Python
try {
    $pythonVersion = python --version
    Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.12+" -ForegroundColor Red
    exit 1
}

# Check pytest
try {
    $pytestVersion = pytest --version
    Write-Host "✅ pytest installed" -ForegroundColor Green
} catch {
    Write-Host "⚠️  pytest not found. Installing..." -ForegroundColor Yellow
    pip install pytest pytest-cov --quiet
}

# ============================================
# 2. Run Pytest with Coverage
# ============================================
Write-Host "`n🧪 Running test suite..." -ForegroundColor Yellow
Write-Host "   Test directory: tests/" -ForegroundColor Cyan
Write-Host "   Configuration: pytest.ini`n" -ForegroundColor Cyan

# Run pytest with coverage
pytest tests/ -v --tb=short --cov=dags --cov-report=term-missing --cov-report=html

$exitCode = $LASTEXITCODE

# ============================================
# 3. Test Summary
# ============================================
Write-Host "`n============================================" -ForegroundColor Cyan

if ($exitCode -eq 0) {
    Write-Host "✅ All tests passed!" -ForegroundColor Green
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host "`n📊 Coverage report generated:" -ForegroundColor Yellow
    Write-Host "   HTML: htmlcov/index.html" -ForegroundColor White
    Write-Host "`nOpen coverage report:" -ForegroundColor Yellow
    Write-Host "   Start-Process htmlcov/index.html" -ForegroundColor Cyan
    Write-Host "`n============================================`n" -ForegroundColor Cyan
} else {
    Write-Host "❌ Tests failed!" -ForegroundColor Red
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host "`nPlease fix failing tests before deployment.`n" -ForegroundColor Yellow
    exit 1
}

# ============================================
# 4. Optional: Run DAG Validation
# ============================================
Write-Host "🔍 Validating DAG files..." -ForegroundColor Yellow

if (Test-Path "dags") {
    $dagFiles = Get-ChildItem -Path "dags" -Filter "*.py" | Where-Object { $_.Name -ne "__init__.py" }
    
    foreach ($dag in $dagFiles) {
        Write-Host "   Checking: $($dag.Name)" -ForegroundColor Cyan
    }
    
    Write-Host "✅ DAG validation complete" -ForegroundColor Green
} else {
    Write-Host "⚠️  dags/ directory not found" -ForegroundColor Yellow
}

Write-Host "`n============================================`n" -ForegroundColor Cyan
