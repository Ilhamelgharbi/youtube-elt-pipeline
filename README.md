# 📊 YouTube Data ELT Pipeline

A production-ready **Extract-Load-Transform (ELT)** pipeline built with **Apache Airflow** that extracts YouTube channel data, loads it into PostgreSQL, and performs automated data quality validation using **Soda Core**.

[![Tests](https://img.shields.io/badge/tests-59%20passing-success)](tests/)
[![Quality Checks](https://img.shields.io/badge/quality%20checks-54%20passing-success)](include/soda/checks/)
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](requirements.txt)
[![Airflow](https://img.shields.io/badge/airflow-2.10.5-orange.svg)](requirements.txt)
[![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-blue.svg)](.github/workflows/)
[![Docker](https://img.shields.io/badge/docker-automated-blue.svg)](Dockerfile)

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Architecture](#-architecture)
- [Features](#-features)
- [Project Structure](#-project-structure)
- [DAGs Documentation](#-dags-documentation)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Automation Scripts](#-automation-scripts)
- [Data Quality](#-data-quality)
- [Testing](#-testing)
- [Database Schema](#-database-schema)
- [CI/CD Pipeline](#-cicd-pipeline)
- [Development](#-development)

---

## 🎯 Overview

This pipeline automates the extraction, transformation, and quality validation of YouTube channel statistics. It demonstrates best practices in data engineering including:

- **ELT Architecture**: Extract → Load → Transform pattern with staging and core layers
- **Data Quality**: Automated validation with 54+ quality checks using Soda Core
- **Testing**: Comprehensive test suite with 59+ unit and integration tests
- **Orchestration**: Airflow DAG dependencies with proper error handling
- **Schema Management**: Multi-schema PostgreSQL design (staging, core)

**Use Cases:**
- Monitor YouTube channel performance metrics
- Track video statistics (views, likes, comments, duration)
- Ensure data quality with automated validation
- Maintain historical data with UPSERT operations

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         AIRFLOW ORCHESTRATION                    │
└─────────────────────────────────────────────────────────────────┘
                                   │
          ┌────────────────────────┼────────────────────────┐
          │                        │                        │
          ▼                        ▼                        ▼
┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐
│   DAG 1: EXTRACT    │  │   DAG 2: LOAD       │  │  DAG 3: QUALITY     │
│  youtube_extract    │─▶│  youtube_load_db    │─▶│youtube_data_quality │
├─────────────────────┤  ├─────────────────────┤  ├─────────────────────┤
│ • Call YouTube API  │  │ • Read JSON files   │  │ • Run Soda checks   │
│ • Parse video data  │  │ • Transform data    │  │ • Validate quality  │
│ • Save to JSON      │  │ • UPSERT to staging │  │ • Generate reports  │
│ • Extract metadata  │  │ • Update core tables│  │ • Alert on failures │
└─────────────────────┘  └─────────────────────┘  └─────────────────────┘
          │                        │                        │
          ▼                        ▼                        ▼
┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐
│   JSON Storage      │  │   PostgreSQL DB     │  │  Quality Reports    │
│ include/youtube_data│  │ staging & core      │  │ include/soda/reports│
└─────────────────────┘  └─────────────────────┘  └─────────────────────┘
```

**Data Flow:**
1. **Extract**: YouTube API → JSON files (raw data preservation)
2. **Load**: JSON → Staging tables (raw data) → Core tables (transformed data)
3. **Transform**: Duration parsing, NULL handling, derived fields
4. **Validate**: Soda Core quality checks across all tables

---

## ✨ Features

### 🔄 Data Pipeline
- ✅ **YouTube API Integration**: Automated data extraction with retry logic
- ✅ **Incremental Loading**: UPSERT operations to handle updates and new records
- ✅ **Data Synchronization**: DELETE orphaned records from staging
- ✅ **Duration Transformation**: Parse ISO 8601 duration to seconds with labeling (short/long)
- ✅ **NULL Handling**: Graceful handling of missing statistics
- ✅ **JSON Archival**: Timestamped raw data preservation

### 🛡️ Data Quality
- ✅ **54 Quality Checks**: Comprehensive validation rules
- ✅ **Schema Validation**: Column presence, data types, constraints
- ✅ **Freshness Checks**: Data recency validation
- ✅ **Completeness Checks**: NULL value monitoring
- ✅ **Validity Checks**: Regex patterns, value ranges, duplicates
- ✅ **Automated Reporting**: JSON reports with timestamps

### 🧪 Testing
- ✅ **59 Tests**: Unit tests, integration tests, DAG validation
- ✅ **96%+ Coverage**: Comprehensive test coverage
- ✅ **Pytest Framework**: Industry-standard testing
- ✅ **CI/CD Ready**: Automated test execution

---

## 📂 Project Structure

```
youtube-elt-pipeline/
├── dags/                              # Airflow DAG definitions
│   ├── youtube_extract.py             # DAG 1: Extract from YouTube API
│   ├── youtube_load_db.py             # DAG 2: Load & Transform to PostgreSQL
│   └── youtube_data_quality.py        # DAG 3: Data quality validation
│
├── tests/                             # Test suite (59 tests)
│   ├── conftest.py                    # Pytest fixtures & configuration
│   ├── test_dag_validation.py         # DAG structure & import tests (12)
│   ├── test_data_quality_rules.py     # Soda quality check tests (13)
│   ├── test_data_transformations.py   # Data transformation tests (6)
│   ├── test_database_operations.py    # UPSERT/DELETE operation tests (9)
│   ├── test_duration_transformations.py # Duration parsing tests (11)
│   └── test_helper_functions.py       # Utility function tests (8)
│
├── include/                           # Additional project resources
│   ├── sql/
│   │   └── create_schemas.sql         # Database schema definitions
│   ├── soda/
│   │   ├── configuration.yml          # Soda Core connection config
│   │   ├── checks/
│   │   │   └── videos_quality.yml     # 54 quality check definitions
│   │   └── reports/                   # Quality check reports (JSON)
│   └── youtube_data/                  # JSON data files (timestamped)
│
├── .env.example                       # Environment variables template
├── .gitignore                         # Git ignore patterns
├── Dockerfile                         # Astro Runtime Docker image
├── requirements.txt                   # Python dependencies
├── packages.txt                       # OS-level packages
├── pytest.ini                         # Pytest configuration
├── airflow_settings.yaml              # Airflow connections & variables
└── README.md                          # This file
```

---

## 🔧 DAGs Documentation

### 1️⃣ **youtube_extract** - Data Extraction

**Purpose**: Extract video data from YouTube API and save to JSON files.

**Schedule**: Daily at 8:00 AM

**Tasks:**
- `create_youtube_data_dir`: Create storage directory for JSON files
- `produce_JSON`: Call YouTube API and extract channel video data

**Key Features:**
- YouTube Data API v3 integration
- Configurable channel ID and API key
- Timestamped JSON files: `{CHANNEL_NAME}_{YYYYMMDD_HHMMSS}.json`
- Extracts: video ID, title, description, publish date, thumbnails, tags, statistics
- Error handling with retries (3 attempts)

**Configuration:**
```python
YOUTUBE_API_KEY = "your_api_key_here"
CHANNEL_ID = "UCX6OQ3DkcsbYNE6H8uQQuVA"  # MrBeast
MAX_RESULTS = 50  # Videos per page
```

---

### 2️⃣ **youtube_load_db** - Data Loading & Transformation

**Purpose**: Load JSON data into PostgreSQL with transformations.

**Schedule**: Runs after `youtube_extract` completes

**Tasks:**
1. `create_schemas`: Create staging and core schemas
2. `create_staging_table`: Create `staging.youtube_videos_raw`
3. `load_staging`: UPSERT JSON data to staging table
4. `create_core_tables`: Create `core.videos` and `core.video_statistics`
5. `update_core_videos`: Transform and load video metadata
6. `update_core_statistics`: Load video statistics
7. `delete_staging`: Clean up processed/deleted videos

**Key Transformations:**
- **Duration Parsing**: Convert ISO 8601 (e.g., `PT4M13S`) to seconds (253)
- **Duration Labeling**: Categorize as "short" (<10 min) or "long" (≥10 min)
- **NULL Handling**: Default 0 for missing statistics (views, likes, comments)
- **Timestamp Conversion**: Parse published_at to proper timestamp
- **Tag Processing**: Handle missing or empty tag arrays

**Database Operations:**
```sql
-- UPSERT pattern (INSERT ... ON CONFLICT DO UPDATE)
INSERT INTO staging.youtube_videos_raw (video_id, title, ...)
VALUES (...)
ON CONFLICT (video_id) DO UPDATE SET ...

-- Synchronization DELETE (remove videos deleted from YouTube)
DELETE FROM staging.youtube_videos_raw
WHERE video_id NOT IN (SELECT video_id FROM current_batch)
```

---

### 3️⃣ **youtube_data_quality** - Quality Validation

**Purpose**: Validate data quality using Soda Core framework.

**Schedule**: Runs after `youtube_load_db` completes

**Tasks:**
- `soda_quality_check`: Execute 54 quality checks across all tables

**Quality Dimensions:**
- **Schema Checks**: Column presence, data types (18 checks)
- **Freshness Checks**: Data recency within 7 days (3 checks)
- **Completeness Checks**: NULL value thresholds (9 checks)
- **Validity Checks**: Positive values, regex patterns (15 checks)
- **Uniqueness Checks**: Primary key duplicates (3 checks)
- **Row Count Checks**: Table synchronization (6 checks)

**Check Examples:**
```yaml
# Duration format validation
checks for staging.youtube_videos_raw:
  - invalid_count(duration_readable) = 0:
      valid regex: '^\d+:\d{2}:\d{2}$|^\d+:\d{2}$'

# Statistics validity
checks for core.video_statistics:
  - invalid_count(view_count) = 0:
      valid min: 0
  - missing_count(like_count) = 0
```

**Output**: JSON reports in `include/soda/reports/quality_report_*.json`

---

## 🔌 Prerequisites

### Required Software
- **Docker Desktop**: For running Airflow locally
- **Astronomer CLI**: For Airflow development
- **PostgreSQL**: Database (included in Docker setup)
- **Python 3.12+**: For local testing

### Required Accounts
- **YouTube Data API v3 Key**: [Get API Key](https://console.cloud.google.com/apis/credentials)
- **PostgreSQL Database**: Connection details (host, port, database, user, password)

---

## 📥 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/Ilhamelgharbi/youtube-elt-pipeline.git
cd youtube-elt-pipeline
```

### 2. Install Astronomer CLI
```bash
# Windows (PowerShell)
winget install -e --id Astronomer.Astro

# macOS
brew install astro

# Linux
curl -sSL install.astronomer.io | sudo bash -s
```

### 3. Install Python Dependencies (for testing)
```bash
pip install -r requirements.txt
```

---

## ⚙️ Configuration

### 1. Environment Variables

Copy the example environment file and configure:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```bash
# YouTube API Configuration
YOUTUBE_API_KEY=your_youtube_api_key_here
CHANNEL_ID=UCX6OQ3DkcsbYNE6H8uQQuVA

# PostgreSQL Configuration
POSTGRES_HOST=host.docker.internal
POSTGRES_PORT=5432
POSTGRES_DB=youtube_data
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=your_db_password

# Airflow Configuration
AIRFLOW_CONN_POSTGRES_DEFAULT=postgresql://user:password@host:5432/database
AIRFLOW_CONN_SODA_POSTGRES=postgresql://user:password@host:5432/database
```

### 2. Airflow Connections

Configure in `airflow_settings.yaml`:

```yaml
connections:
  - conn_id: postgres_default
    conn_type: postgres
    conn_host: host.docker.internal
    conn_port: 5432
    conn_schema: youtube_data
    conn_login: your_user
    conn_password: your_password

  - conn_id: soda_postgres
    conn_type: postgres
    conn_host: host.docker.internal
    conn_port: 5432
    conn_schema: youtube_data
    conn_login: your_user
    conn_password: your_password
```

### 3. Soda Core Configuration

Update `include/soda/configuration.yml`:

```yaml
data_source postgres:
  type: postgres
  host: ${POSTGRES_HOST}
  port: ${POSTGRES_PORT}
  username: ${POSTGRES_USER}
  password: ${POSTGRES_PASSWORD}
  database: ${POSTGRES_DB}
  schema: staging
```

---

## 🚀 Usage

### Start Airflow Locally

```bash
astro dev start
```

This command starts 5 Docker containers:
- **Postgres**: Airflow metadata database (port 5432)
- **Webserver**: Airflow UI (http://localhost:8080)
- **Scheduler**: DAG orchestration
- **Triggerer**: Deferred tasks
- **DAG Processor**: DAG parsing

**Access Airflow UI**: http://localhost:8080
- Username: `admin`
- Password: `admin`

### Run DAGs Manually

1. Navigate to http://localhost:8080
2. Enable the DAGs:
   - `youtube_extract`
   - `youtube_load_db`
   - `youtube_data_quality`
3. Trigger `youtube_extract` (others will run automatically via dependencies)

### Monitor Pipeline

- **DAGs View**: Check execution status, task duration, success/failure
- **Graph View**: Visualize task dependencies
- **Logs**: Click on tasks to view detailed logs
- **Quality Reports**: Check `include/soda/reports/` for validation results

### Stop Airflow

```bash
astro dev stop
```

---

## �️ Automation Scripts

The project includes PowerShell automation scripts in the `scripts/` directory for streamlined deployment, testing, and data management.

### Available Scripts

#### 1. **setup.ps1** - Initial Project Setup ⚙️

Automates the complete initial setup of the project.

```powershell
.\scripts\setup.ps1
```

**What it does:**
- ✅ Checks Docker, Astro CLI, and Python installation
- ✅ Creates `.env` file from `.env.example`
- ✅ Creates required directories (`include/youtube_data`, `include/soda/reports`, `logs`)
- ✅ Installs Python dependencies from `requirements.txt`
- ✅ Starts Airflow with `astro dev start`
- ✅ Displays access information and next steps

**Use when:** Setting up the project for the first time.

---

#### 2. **test.ps1** - Run All Tests 🧪

Executes the complete test suite with coverage reporting.

```powershell
.\scripts\test.ps1
```

**What it does:**
- ✅ Checks pytest installation (installs if missing)
- ✅ Runs all 59 tests in `tests/` directory
- ✅ Generates coverage report (terminal + HTML)
- ✅ Validates DAG file structure
- ✅ Color-coded output for easy reading

**Output:**
- Terminal: Test results with coverage percentage
- HTML: `htmlcov/index.html` (detailed coverage report)

**Use when:** Validating code changes, before commits, or CI/CD integration.

---

#### 3. **copy_data.ps1** - Data Synchronization 📦

Manages file synchronization between Docker container and local filesystem.

```powershell
# Copy Airflow logs from container to host
.\scripts\copy_data.ps1 logs

# Copy JSON data files from container to host
.\scripts\copy_data.ps1 json

# Copy Soda quality reports from container to host
.\scripts\copy_data.ps1 reports

# Copy custom file to container
.\scripts\copy_data.ps1 to-container include/youtube_data/custom.json

# Copy custom file from container
.\scripts\copy_data.ps1 from-container /usr/local/airflow/logs
```

**Available Actions:**
| Action | Description |
|--------|-------------|
| `logs` | Copy Airflow logs from container to `logs_backup_<timestamp>/` |
| `json` | Copy JSON data files to `include/youtube_data/` |
| `reports` | Copy Soda quality reports to `include/soda/reports/` |
| `to-container [path]` | Copy file/folder from host to container |
| `from-container [path]` | Copy file/folder from container to host |

**Use when:** Backing up data, extracting logs for debugging, or synchronizing files.

---

#### 4. **deploy.ps1** - Deployment Automation 🚀

Manages Airflow deployment, restart, and status monitoring.

```powershell
# Start Airflow locally (first time or after stop)
.\scripts\deploy.ps1 local

# Restart all Airflow services
.\scripts\deploy.ps1 restart

# Rebuild Docker images and restart
.\scripts\deploy.ps1 build

# Check current status and access points
.\scripts\deploy.ps1 status

# Stop all Airflow containers
.\scripts\deploy.ps1 stop
```

**Available Actions:**
| Action | Description |
|--------|-------------|
| `local` | Start Airflow locally (default action) |
| `restart` | Stop and restart all Airflow services |
| `build` | Rebuild Docker images from scratch and restart |
| `status` | Display container status, access points, and data counts |
| `stop` | Stop all Airflow containers |

**Use when:** Starting/stopping Airflow, applying configuration changes, or troubleshooting.

---

### Quick Start Workflow

**First Time Setup:**
```powershell
# 1. Run automated setup
.\scripts\setup.ps1

# 2. Edit environment variables with your API keys
notepad .env

# 3. Restart to apply configuration
.\scripts\deploy.ps1 restart

# 4. Run tests to verify everything works
.\scripts\test.ps1
```

**Daily Development:**
```powershell
# Start Airflow
.\scripts\deploy.ps1 local

# Make code changes...

# Run tests
.\scripts\test.ps1

# Copy data for analysis
.\scripts\copy_data.ps1 json
.\scripts\copy_data.ps1 reports

# Stop when done
.\scripts\deploy.ps1 stop
```

**Before Deployment/Submission:**
```powershell
# 1. Run all tests
.\scripts\test.ps1

# 2. Check Airflow status
.\scripts\deploy.ps1 status

# 3. Backup important data
.\scripts\copy_data.ps1 json
.\scripts\copy_data.ps1 reports
.\scripts\copy_data.ps1 logs
```

---

### Script Requirements

All scripts require:
- **Windows PowerShell 5.1+** or **PowerShell Core 7+**
- **Docker Desktop** running
- **Astro CLI** installed
- **Python 3.12+** (for testing)

**Troubleshooting:**

If you get "execution policy" errors:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

For detailed script documentation, see [`scripts/README.md`](scripts/README.md).

---

## �🛡️ Data Quality

### Quality Check Categories

| Category | Checks | Description |
|----------|--------|-------------|
| **Schema Validation** | 18 | Column presence, data types, constraints |
| **Freshness** | 3 | Data recency (within 7 days) |
| **Completeness** | 9 | NULL value thresholds |
| **Validity** | 15 | Value ranges, regex patterns |
| **Uniqueness** | 3 | Primary key duplicates |
| **Row Counts** | 6 | Table synchronization |
| **TOTAL** | **54** | **100% Passing** |

### Running Quality Checks

**Via Airflow DAG:**
```bash
# Trigger via UI or CLI
astro dev run dags trigger youtube_data_quality
```

**Standalone (local testing):**
```bash
soda scan -d postgres -c include/soda/configuration.yml include/soda/checks/videos_quality.yml
```

### Quality Reports

Reports are saved to `include/soda/reports/quality_report_YYYYMMDD_HHMMSS.json`

Example report structure:
```json
{
  "timestamp": "2024-10-03T14:36:21Z",
  "checks_evaluated": 54,
  "checks_passed": 54,
  "checks_failed": 0,
  "checks_warned": 0,
  "exit_code": 0
}
```

---

## 🧪 Testing

### Run All Tests

```bash
# Run full test suite (59 tests)
pytest

# Run with coverage report
pytest --cov=dags --cov-report=html

# Run specific test file
pytest tests/test_dag_validation.py
```

### Test Categories

| Test File | Tests | Description |
|-----------|-------|-------------|
| `test_dag_validation.py` | 12 | DAG structure, imports, dependencies |
| `test_data_quality_rules.py` | 13 | Soda quality check validation |
| `test_data_transformations.py` | 6 | Data transformation logic |
| `test_database_operations.py` | 9 | UPSERT/DELETE operations |
| `test_duration_transformations.py` | 11 | Duration parsing & labeling |
| `test_helper_functions.py` | 8 | Utility functions |
| **TOTAL** | **59** | **100% Passing** |

### Test Coverage

- **Unit Tests**: 46 tests (78%)
- **Integration Tests**: 7 tests (12%)
- **DAG Validation Tests**: 12 tests (20%)

**Coverage**: 96%+ across all DAG files

---

## 🗄️ Database Schema

### Staging Layer

#### `staging.youtube_videos_raw`
Raw data from YouTube API (904 rows)

| Column | Type | Description |
|--------|------|-------------|
| `video_id` | VARCHAR(20) PK | YouTube video ID |
| `title` | TEXT | Video title |
| `description` | TEXT | Video description |
| `published_at` | TIMESTAMP | Publication timestamp |
| `channel_id` | VARCHAR(50) | YouTube channel ID |
| `channel_title` | VARCHAR(200) | Channel name |
| `tags` | TEXT[] | Video tags array |
| `duration` | VARCHAR(50) | ISO 8601 duration (PT4M13S) |
| `duration_readable` | VARCHAR(20) | Human-readable (4:13) |
| `thumbnail_url` | TEXT | Video thumbnail URL |
| `view_count` | BIGINT | View count |
| `like_count` | BIGINT | Like count |
| `comment_count` | BIGINT | Comment count |

### Core Layer

#### `core.videos`
Transformed video metadata (904 rows)

| Column | Type | Description |
|--------|------|-------------|
| `video_id` | VARCHAR(20) PK | YouTube video ID |
| `title` | TEXT | Video title |
| `description` | TEXT | Video description |
| `published_at` | TIMESTAMP | Publication timestamp |
| `channel_id` | VARCHAR(50) | YouTube channel ID |
| `channel_title` | VARCHAR(200) | Channel name |
| `tags` | TEXT[] | Video tags array |
| `duration_seconds` | INTEGER | Duration in seconds |
| `duration_label` | VARCHAR(10) | "short" or "long" |
| `thumbnail_url` | TEXT | Video thumbnail URL |

#### `core.video_statistics`
Video performance metrics (904 rows)

| Column | Type | Description |
|--------|------|-------------|
| `video_id` | VARCHAR(20) PK FK | YouTube video ID |
| `view_count` | BIGINT | View count (defaults to 0) |
| `like_count` | BIGINT | Like count (defaults to 0) |
| `comment_count` | BIGINT | Comment count (defaults to 0) |

**Data Distribution:**
- **Short videos** (<10 min): 144 videos (16%)
- **Long videos** (≥10 min): 760 videos (84%)

---

## � CI/CD Pipeline

The project includes automated GitHub Actions workflows for continuous integration and deployment.

### Workflows

#### **CI - Tests & Validation** 
Runs automatically on every push and pull request to `main` or `develop` branches.

**Jobs:**
1. **🔍 Lint Code** - Code quality checks with flake8 and black
2. **🧪 Run Tests** - Execute all 59 tests with coverage reporting
3. **✅ Validate DAGs** - Airflow DAG syntax and structure validation
4. **🔒 Security Scan** - Dependency vulnerability checking
5. **📊 Build Summary** - Aggregated results and status

**Trigger manually:**
```bash
# Via GitHub UI: Actions tab → CI - Tests & Validation → Run workflow
```

#### **Docker Build**
Builds and validates Docker image on release tags.

**Jobs:**
1. **🐳 Build Docker Image** - Multi-platform build with caching
2. **🧪 Test Docker Image** - Validate image functionality

**Trigger on release:**
```bash
git tag v1.0.0
git push origin v1.0.0
```

### Viewing Results

1. Go to **Actions** tab on GitHub repository
2. Click on a workflow run to see detailed logs
3. Check **Summary** for quick overview
4. Review coverage reports and DAG validation

**Workflow files:** [`.github/workflows/`](.github/workflows/)

---

## �💻 Development

### Local Development Setup

```bash
# Start Airflow
astro dev start

# Access Airflow bash
astro dev bash

# Run pytest inside container
astro dev pytest

# View logs
astro dev logs
```

### Adding New Quality Checks

Edit `include/soda/checks/videos_quality.yml`:

```yaml
checks for staging.youtube_videos_raw:
  - row_count > 0
  - missing_count(video_id) = 0
  - duplicate_count(video_id) = 0
  # Add your custom checks here
```

### Modifying DAGs

1. Edit DAG files in `dags/`
2. Save changes (auto-reload in 30 seconds)
3. Check Airflow UI for errors
4. Run tests: `pytest tests/`

### Database Migrations

```sql
-- Run SQL scripts via psql or Airflow task
psql -h localhost -U postgres -d youtube_data -f include/sql/create_schemas.sql
```

---

## 📊 Performance Metrics

- **Extraction Time**: ~2-3 minutes (50 videos per API call)
- **Load Time**: ~1-2 minutes (UPSERT 900+ records)
- **Quality Checks**: ~30 seconds (54 checks)
- **Total Pipeline Duration**: ~5-7 minutes end-to-end

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Write tests for new functionality
4. Ensure all tests pass: `pytest`
5. Commit changes: `git commit -m "Add your feature"`
6. Push to branch: `git push origin feature/your-feature`
7. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License.

---

## 👤 Author

**Ilham El Gharbi**
- GitHub: [@Ilhamelgharbi](https://github.com/Ilhamelgharbi)
- Repository: [youtube-elt-pipeline](https://github.com/Ilhamelgharbi/youtube-elt-pipeline)

---

## 🙏 Acknowledgments

- **Apache Airflow**: Workflow orchestration
- **Astronomer**: Airflow development platform
- **Soda Core**: Data quality framework
- **YouTube Data API**: Data source
- **PostgreSQL**: Database system

---

## 📞 Support

For questions or issues:
- Open an issue on [GitHub](https://github.com/Ilhamelgharbi/youtube-elt-pipeline/issues)
- Check [Airflow Documentation](https://airflow.apache.org/docs/)
- Review [Soda Core Documentation](https://docs.soda.io/)

---

**⭐ If you find this project useful, please give it a star!**
