# 📋 YouTube ELT Pipeline - Project Requirements

**Project**: YouTube ELT Data Pipeline with Apache Airflow  
**Date**: October 2, 2025  
**Status**: Phase 4 Complete ✅

---

## 🎯 Project Overview

Automated ELT (Extract-Load-Transform) pipeline that:
1. Extracts YouTube video data via YouTube Data API v3
2. Loads data into PostgreSQL data warehouse
3. Validates data quality using Soda Core
4. Provides automated testing and CI/CD

---

## 🛠️ Technology Stack

### Core Technologies
| Technology | Version | Purpose |
|------------|---------|---------|
| **Apache Airflow** | 2.10.x+ | Workflow orchestration |
| **Astro Runtime** | 3.0-11 | Airflow distribution |
| **Python** | 3.12 | Programming language |
| **PostgreSQL** | 12.6 | Data warehouse |
| **Docker** | Latest | Containerization |
| **Soda Core** | 3.0.45 | Data quality validation |

---

## 📦 Python Dependencies

### requirements.txt
```txt
# YouTube API
google-api-python-client==2.108.0    # YouTube Data API v3 client
google-auth==2.23.4                  # Google authentication
isodate==0.6.1                       # ISO 8601 duration parsing

# PostgreSQL
psycopg2-binary==2.9.9               # PostgreSQL adapter
apache-airflow-providers-postgres==5.7.1  # Airflow PostgreSQL provider

# Data Processing
pandas==2.1.3                        # Data manipulation
numpy==1.26.0                        # Numerical computing

# Testing
pytest==7.4.3                        # Unit testing framework
```

### Dockerfile Installations
```dockerfile
# Python 3.12 Compatibility
setuptools                           # Provides distutils module

# Data Quality
soda-core-postgres==3.0.45          # Soda Core for PostgreSQL (no scientific package)
```

**Note**: Soda Core is installed in Dockerfile (not requirements.txt) to:
- Avoid dependency conflicts with Astro Runtime
- Reduce build time by excluding soda-core-scientific package
- Ensure Python 3.12 compatibility with setuptools

---

## 🗄️ Database Schema

### Database: `youtube_dwh`

#### Schema: `staging`
**Table: `youtube_videos_raw`**
```sql
CREATE TABLE staging.youtube_videos_raw (
    id SERIAL PRIMARY KEY,
    video_id VARCHAR(11) NOT NULL,
    title TEXT,
    description TEXT,
    published_at TIMESTAMP,
    channel_id VARCHAR(24),
    channel_title VARCHAR(255),
    channel_handle VARCHAR(255),
    view_count BIGINT,
    like_count BIGINT,
    comment_count BIGINT,
    duration INTEGER,  -- in seconds
    tags TEXT[],
    category_id VARCHAR(10),
    extraction_date TIMESTAMP DEFAULT NOW(),
    raw_json JSONB
);
```

#### Schema: `core`
**Table: `videos`**
```sql
CREATE TABLE core.videos (
    video_id VARCHAR(11) PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    published_at TIMESTAMP NOT NULL,
    channel_id VARCHAR(24) NOT NULL,
    channel_title VARCHAR(255),
    channel_handle VARCHAR(255),
    duration INTEGER,
    category_id VARCHAR(10),
    tags TEXT[],
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**Table: `video_statistics`**
```sql
CREATE TABLE core.video_statistics (
    id SERIAL PRIMARY KEY,
    video_id VARCHAR(11) REFERENCES core.videos(video_id),
    view_count BIGINT DEFAULT 0,
    like_count BIGINT DEFAULT 0,
    comment_count BIGINT DEFAULT 0,
    recorded_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🔑 Environment Variables

### Required Variables (.env)
```env
# YouTube API Configuration
YOUTUBE_API_KEY=<your-api-key>              # YouTube Data API v3 key
YOUTUBE_CHANNEL_ID=UCX6OQ3DkcsbYNE6H8uQQuVA # Target channel ID
YOUTUBE_CHANNEL_HANDLE=MrBeast               # Target channel handle
YOUTUBE_MAX_RESULTS=50                       # Videos per extraction

# PostgreSQL Configuration
POSTGRES_HOST=postgres                       # Docker service name
POSTGRES_PORT=5432                          # PostgreSQL port
POSTGRES_DB=youtube_dwh                     # Database name
POSTGRES_USER=postgres                      # Database user
POSTGRES_PASSWORD=postgres                  # Database password
```

### How to Obtain YouTube API Key
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable **YouTube Data API v3**
4. Create credentials → API Key
5. Copy key to `.env` file

---

## 📂 Project Structure

```
version-final/
├── dags/                           # Airflow DAGs
│   ├── youtube_extract.py          # Phase 1: Extract YouTube data
│   ├── youtube_load_db.py          # Phase 2: Load to PostgreSQL
│   └── youtube_data_quality.py     # Phase 4: Data quality validation
│
├── include/                        # Data and configurations
│   ├── config/                     # Configuration files
│   ├── sql/
│   │   └── create_schemas.sql      # Database initialization
│   ├── youtube_data/               # Extracted JSON files
│   └── soda/                       # Soda Core configurations
│       ├── configuration.yml       # PostgreSQL connection
│       ├── checks/
│       │   └── videos_quality.yml  # 22 quality check rules
│       ├── results/                # Scan log files
│       └── reports/                # JSON quality reports
│
├── plugins/                        # Airflow plugins (empty)
├── tests/                          # Unit tests
│   └── dags/
│       └── test_dag_example.py     # Sample test
│
├── Dockerfile                      # Docker image configuration
├── requirements.txt                # Python dependencies
├── packages.txt                    # System packages (empty)
├── .env                           # Environment variables
├── docker-compose.override.yml.backup  # Disabled override file
│
└── Documentation/
    ├── PROJECT_GUIDE.md            # Step-by-step guide
    ├── BEGINNER_GUIDE.md           # Beginner tutorial
    ├── PHASE3_COMPLETE.md          # Phase 3 documentation
    ├── PHASE4_COMPLETE.md          # Phase 4 documentation
    └── PROJECT_REQUIREMENTS.md     # This file
```

---

## 🔄 DAG Requirements

### DAG 1: youtube_extract
**Purpose**: Extract YouTube video data via API  
**Schedule**: Manual trigger  
**Tasks**:
1. `extract_videos` - Call YouTube API, save JSON files

**Output**: `include/youtube_data/<channel>_<timestamp>.json`

**Required**:
- YouTube API key
- Channel ID or handle
- Internet connection

---

### DAG 2: youtube_load_db
**Purpose**: Load JSON data into PostgreSQL  
**Schedule**: Manual trigger  
**Tasks**:
1. `init_database` - Create schemas and tables
2. `load_staging` - Load JSON to staging.youtube_videos_raw
3. `transform_core` - Transform to core.videos (UPSERT)
4. `load_statistics` - Load to core.video_statistics (APPEND)

**Required**:
- PostgreSQL running
- JSON files in `include/youtube_data/`
- Database connection details

---

### DAG 3: youtube_data_quality
**Purpose**: Validate data quality with Soda Core  
**Schedule**: Manual trigger  
**Tasks**:
1. `prepare_soda_environment` - Validate config files
2. `run_soda_scan` - Execute Soda Core CLI scan
3. `analyze_scan_results` - Parse logs, generate reports
4. `additional_validations` - Custom SQL checks

**Required**:
- Soda Core installed (via Dockerfile)
- Configuration files in `include/soda/`
- Data in core schema tables

**Quality Checks**: 22 checks
- 12 checks for `core.videos`
- 10 checks for `core.video_statistics`

---

## 💻 System Requirements

### Hardware
- **CPU**: 2+ cores recommended
- **RAM**: 4GB minimum, 8GB recommended
- **Disk**: 10GB free space
- **Network**: Stable internet connection

### Software
- **OS**: Windows 10/11, macOS, or Linux
- **Docker Desktop**: Latest version with WSL2 (Windows)
- **Astro CLI**: 1.x or higher
- **Git**: For version control
- **Code Editor**: VS Code recommended

---

## 🚀 Installation & Setup

### 1. Prerequisites
```powershell
# Install Astro CLI
winget install -e --id Astronomer.Astro

# Verify installation
astro version

# Install Docker Desktop
# Download from: https://www.docker.com/products/docker-desktop/
```

### 2. Clone/Setup Project
```powershell
# Navigate to project directory
cd C:\Users\user\Desktop\version-final

# Initialize Astro (if new project)
astro dev init

# Configure .env file
# Add YouTube API key and other variables
```

### 3. Build & Start
```powershell
# Build Docker image (includes Soda Core)
astro dev start

# Verify containers
docker ps

# Expected containers:
# - scheduler
# - api-server
# - dag-processor
# - triggerer
# - postgres
```

### 4. Access Airflow UI
- **URL**: http://localhost:8080
- **Username**: admin
- **Password**: admin

---

## 🧪 Testing Requirements

### Unit Tests (Phase 5 - Planned)
```bash
# Run all tests
pytest tests/

# Run specific test
pytest tests/dags/test_youtube_extract.py -v
```

**Test Coverage**:
- DAG integrity (imports, structure)
- Task execution logic
- Database connections
- Data transformations
- Soda Core checks

---

## 📊 Data Quality Requirements

### Quality Dimensions
1. **Completeness**: No missing critical fields
2. **Validity**: Data formats and ranges correct
3. **Uniqueness**: No duplicate primary keys
4. **Freshness**: Data is recent and up-to-date
5. **Referential Integrity**: Foreign keys valid
6. **Business Logic**: Domain rules enforced

### Quality Thresholds
| Check Type | Threshold | Action |
|------------|-----------|--------|
| Missing video_id | 0% | FAIL |
| Duplicate video_id | 0% | FAIL |
| Invalid video_id length | 0% | FAIL |
| Likes > Views | 0% | FAIL |
| Statistics age | < 24 hours | WARN |
| Video age | < 365 days | WARN |

---

## 🔒 Security Requirements

### API Keys
- ✅ Stored in `.env` file (not committed to Git)
- ✅ Loaded as environment variables
- ✅ Never hardcoded in source code

### Database
- ✅ Password in `.env` file
- ✅ PostgreSQL isolated in Docker network
- ✅ No external access (localhost only)

### Docker
- ✅ Non-root user (astro) for Airflow processes
- ✅ Minimal base image (Astro Runtime)
- ✅ No unnecessary packages installed

---

## 📈 Performance Requirements

### Build Time
- **Target**: < 3 minutes
- **Actual**: ~2 minutes ✅
- **Optimization**: Removed soda-core-scientific package

### DAG Execution
| DAG | Target Time | Actual Time |
|-----|-------------|-------------|
| youtube_extract | < 30 seconds | ~10 seconds ✅ |
| youtube_load_db | < 2 minutes | ~45 seconds ✅ |
| youtube_data_quality | < 1 minute | ~10 seconds ✅ |

### Database
- **Connection pool**: 5 connections
- **Query timeout**: 60 seconds
- **Batch size**: 1000 rows

---

## 🎯 Success Criteria

### Phase 1-2: Extract & Load ✅
- [x] YouTube API extracts 50 videos
- [x] JSON files saved correctly
- [x] Database schemas created
- [x] Data loaded to staging table
- [x] Data transformed to core tables
- [x] UPSERT logic working (no duplicates)

### Phase 4: Data Quality ✅
- [x] Soda Core installed successfully
- [x] Configuration files valid
- [x] All 22 quality checks passing
- [x] Scan logs generated
- [x] Build time < 3 minutes

### Phase 5: Testing (Planned)
- [ ] 20+ unit tests written
- [ ] 100% DAG import success
- [ ] Test coverage > 80%
- [ ] CI/CD pipeline configured

---

## 🐛 Known Issues & Workarounds

### Issue 1: Docker Compose Override Conflict
**Problem**: Containers won't start with override file  
**Solution**: Rename `docker-compose.override.yml` to `.backup` ✅

### Issue 2: Python 3.12 Distutils Missing
**Problem**: Soda Core requires distutils (removed in Python 3.12)  
**Solution**: Install setuptools in Dockerfile ✅

### Issue 3: Slow Build Times
**Problem**: soda-core-scientific adds 8+ minutes  
**Solution**: Install only soda-core-postgres ✅

### Issue 4: Network Timeouts
**Problem**: Pip downloads timeout after 30 seconds  
**Solution**: Add `--default-timeout=300` flag ✅

---

## 📚 Documentation Requirements

### Required Documentation
- [x] PROJECT_GUIDE.md - Step-by-step implementation guide
- [x] BEGINNER_GUIDE.md - Tutorial for beginners
- [x] PHASE3_COMPLETE.md - Phase 3 completion report
- [x] PHASE4_COMPLETE.md - Phase 4 completion report
- [x] PROJECT_REQUIREMENTS.md - This file
- [x] README.md - Project overview
- [ ] API_DOCUMENTATION.md - API reference (planned)

### Code Documentation
- [x] Inline comments in DAG files
- [x] Docstrings for functions
- [x] SQL comments in schema files
- [x] YAML comments in Soda checks

---

## 🔜 Future Requirements (Phase 5+)

### Phase 5: Testing
- Unit tests for all DAGs
- Integration tests
- Data validation tests
- Mock YouTube API responses

### Phase 6: CI/CD
- GitHub Actions workflow
- Automated testing on push
- Docker image building
- Deployment automation

### Phase 7: Monitoring
- Airflow alerting
- Quality score dashboard
- Performance metrics
- Error tracking

---

## 📞 Support & Resources

### Official Documentation
- [Astro CLI](https://docs.astronomer.io/astro/cli/overview)
- [Apache Airflow](https://airflow.apache.org/docs/)
- [Soda Core](https://docs.soda.io/soda-core/overview.html)
- [YouTube Data API](https://developers.google.com/youtube/v3)

### Project Files
- All documentation in project root
- Code comments in DAG files
- Configuration examples in `include/`

---

## ✅ Requirements Checklist

### Infrastructure
- [x] Docker Desktop installed
- [x] Astro CLI installed
- [x] PostgreSQL container running
- [x] Airflow UI accessible

### Code
- [x] 3 DAGs implemented
- [x] Database schemas defined
- [x] Soda Core checks configured
- [x] Environment variables set

### Data Quality
- [x] 22 quality checks defined
- [x] All checks passing (100%)
- [x] Scan logs generated
- [x] Reports automated

### Documentation
- [x] Project guide complete
- [x] Beginner guide complete
- [x] Phase documentation complete
- [x] Requirements documented

---

**Status**: Phase 4 Complete ✅  
**Next Phase**: Phase 5 - Testing & CI/CD  
**Overall Progress**: 60% (4 of 7 phases complete)
