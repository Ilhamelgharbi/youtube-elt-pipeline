# 🛠️ Automation Scripts

This directory contains PowerShell automation scripts for the YouTube ELT Pipeline project.

## 📋 Available Scripts

### 1. **setup.ps1** - Initial Project Setup
Automates the initial setup of the project including prerequisites checking, environment configuration, and Airflow startup.

**Usage:**
```powershell
.\scripts\setup.ps1
```

**What it does:**
- ✅ Checks Docker, Astro CLI, and Python installation
- ✅ Creates `.env` file from `.env.example`
- ✅ Creates required directories (`include/youtube_data`, `include/soda/reports`, `logs`)
- ✅ Installs Python dependencies
- ✅ Starts Airflow with `astro dev start`

---

### 2. **test.ps1** - Run All Tests
Executes the complete test suite with coverage reporting.

**Usage:**
```powershell
.\scripts\test.ps1
```

**What it does:**
- ✅ Checks pytest installation
- ✅ Runs all tests in `tests/` directory
- ✅ Generates coverage report (terminal + HTML)
- ✅ Validates DAG files

**Output:**
- Terminal: Test results with coverage percentage
- HTML: `htmlcov/index.html` (detailed coverage report)

---

### 3. **copy_data.ps1** - Copy Files Between Container and Host
Manages data synchronization between Docker container and local filesystem.

**Usage:**
```powershell
# Copy logs from container to host
.\scripts\copy_data.ps1 logs

# Copy JSON data files
.\scripts\copy_data.ps1 json

# Copy Soda quality reports
.\scripts\copy_data.ps1 reports

# Copy custom file to container
.\scripts\copy_data.ps1 to-container include/youtube_data/custom.json

# Copy custom file from container
.\scripts\copy_data.ps1 from-container /usr/local/airflow/logs
```

**Available actions:**
- `logs` - Copy Airflow logs from container
- `json` - Copy JSON data files from container
- `reports` - Copy Soda quality reports from container
- `to-container [path]` - Copy file/folder to container
- `from-container [path]` - Copy file/folder from container

---

### 4. **deploy.ps1** - Deployment Automation
Manages Airflow deployment, restart, and status checking.

**Usage:**
```powershell
# Deploy locally (start Airflow)
.\scripts\deploy.ps1 local

# Restart Airflow services
.\scripts\deploy.ps1 restart

# Rebuild Docker images
.\scripts\deploy.ps1 build

# Check current status
.\scripts\deploy.ps1 status

# Stop Airflow
.\scripts\deploy.ps1 stop
```

**Available actions:**
- `local` - Start Airflow locally (default)
- `restart` - Restart all Airflow services
- `build` - Rebuild Docker images and restart
- `status` - Show current status and access points
- `stop` - Stop all Airflow containers

---

## 🚀 Quick Start Workflow

### First Time Setup:
```powershell
# 1. Run setup (installs dependencies, starts Airflow)
.\scripts\setup.ps1

# 2. Edit .env with your API keys
notepad .env

# 3. Restart to apply configuration
.\scripts\deploy.ps1 restart

# 4. Run tests to verify everything works
.\scripts\test.ps1
```

### Daily Development:
```powershell
# Start Airflow
.\scripts\deploy.ps1 local

# Run tests after code changes
.\scripts\test.ps1

# Copy data for analysis
.\scripts\copy_data.ps1 json
.\scripts\copy_data.ps1 reports

# Stop when done
.\scripts\deploy.ps1 stop
```

---

## 📝 Requirements

All scripts require:
- **Windows PowerShell 5.1+** or **PowerShell Core 7+**
- **Docker Desktop** running
- **Astro CLI** installed
- **Python 3.12+** (for testing)

---

## 🔧 Troubleshooting

### "Execution policy" error
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Docker not running
Start Docker Desktop and wait for it to fully start, then retry.

### Astro CLI not found
```powershell
winget install -e --id Astronomer.Astro
```

### Container name mismatch
If your container has a different name, update `$CONTAINER_NAME` in `copy_data.ps1`.

---

## 📄 License

Part of the YouTube ELT Pipeline project.
