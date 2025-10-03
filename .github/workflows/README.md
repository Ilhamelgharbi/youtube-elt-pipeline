# 🚀 GitHub Actions CI/CD Workflows

This directory contains automated workflows for continuous integration and deployment of the YouTube ELT Pipeline.

## 📋 Available Workflows

### 1. **ci.yml** - Continuous Integration ✅

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`
- Manual trigger via GitHub Actions UI

**What it does:**

#### 🔍 **Job 1: Lint Code**
- Runs `flake8` for Python syntax checking
- Runs `black` for code formatting validation
- Ensures code quality and consistency

#### 🧪 **Job 2: Run Tests**
- Executes all 59 tests with `pytest`
- Generates coverage report (XML + HTML)
- Uploads coverage to Codecov (optional)
- Creates coverage summary in GitHub

#### ✅ **Job 3: Validate DAGs**
- Loads all Airflow DAGs using `DagBag`
- Checks for import errors
- Validates DAG structure and dependencies
- Detects cycles in task dependencies

#### 🔒 **Job 4: Security Scan**
- Scans dependencies for known vulnerabilities
- Uses `safety` to check for security issues
- Generates security report

#### 📊 **Job 5: Build Summary**
- Aggregates results from all jobs
- Creates comprehensive summary in GitHub Actions
- Shows status of each job (✅/❌)

**Status Badge:**
```markdown
![CI](https://github.com/Ilhamelgharbi/youtube-elt-pipeline/workflows/CI%20-%20Tests%20%26%20Validation/badge.svg)
```

---

### 2. **docker-build.yml** - Docker Build & Validation 🐳

**Triggers:**
- Release tags (e.g., `v1.0.0`)
- Published releases
- Manual trigger via GitHub Actions UI

**What it does:**

#### 🐳 **Job 1: Build Docker Image**
- Builds Docker image from `Dockerfile`
- Uses Docker Buildx for advanced features
- Extracts metadata (tags, labels)
- Caches layers for faster builds

#### 🧪 **Job 2: Test Docker Image**
- Validates Python version in image
- Checks installed packages (Airflow, Soda, etc.)
- Ensures image is functional

**Use case:** Validate Docker image before deployment or release.

---

## 🚀 Workflow Execution

### Running Workflows Automatically

Workflows run automatically on:
- **Every push** to `main` or `develop`
- **Every pull request** to `main` or `develop`
- **New release** tags

### Running Workflows Manually

1. Go to **Actions** tab on GitHub
2. Select the workflow (CI or Docker Build)
3. Click **Run workflow**
4. Choose branch and click **Run workflow**

---

## 📊 Monitoring Workflows

### View Results

1. Navigate to **Actions** tab in GitHub repository
2. Click on a workflow run to see details
3. View each job's logs and results
4. Check the **Summary** for quick overview

### Status Checks

Each job produces status indicators:
- ✅ Success - All checks passed
- ❌ Failure - One or more checks failed
- ⚠️ Warning - Non-critical issues detected
- ⏭️ Skipped - Job was skipped

---

## 🔧 Workflow Configuration

### Customizing Triggers

Edit the `on:` section in workflow files:

```yaml
on:
  push:
    branches:
      - main
      - develop
      - feature/*  # Add feature branches
  pull_request:
    branches:
      - main
```

### Adding Secrets

For workflows that need credentials:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Add secrets like:
   - `DOCKER_USERNAME`
   - `DOCKER_PASSWORD`
   - `CODECOV_TOKEN` (optional)

### Modifying Jobs

To add/modify jobs, edit the workflow YAML files:

```yaml
jobs:
  my-custom-job:
    name: 🎯 Custom Job
    runs-on: ubuntu-latest
    steps:
      - name: Run custom script
        run: ./scripts/custom.sh
```

---

## 📈 Best Practices

### ✅ **Do:**
- Keep workflows fast (< 10 minutes)
- Use caching for dependencies
- Fail fast on critical errors
- Add meaningful job names and emojis
- Document workflow purposes

### ❌ **Don't:**
- Commit secrets to workflow files
- Run expensive operations on every commit
- Ignore security scan warnings
- Skip testing before merging

---

## 🐛 Troubleshooting

### Common Issues

**Issue**: Workflow fails on DAG validation
- **Fix**: Check `dags/` for syntax errors
- **Command**: Run locally: `python -m pytest tests/test_dag_validation.py`

**Issue**: Tests fail in CI but pass locally
- **Fix**: Check Python version consistency (3.12)
- **Fix**: Ensure all dependencies in `requirements.txt`

**Issue**: Lint errors
- **Fix**: Run locally: `flake8 dags/`
- **Fix**: Format code: `black dags/ tests/`

**Issue**: Security vulnerabilities detected
- **Fix**: Update dependencies: `pip install --upgrade -r requirements.txt`
- **Fix**: Check `safety check` output

---

## 📊 Workflow Performance

### Typical Run Times

| Workflow | Jobs | Duration |
|----------|------|----------|
| **CI - Tests & Validation** | 5 jobs | ~3-5 minutes |
| **Docker Build** | 2 jobs | ~2-3 minutes |

### Optimization Tips

1. **Use caching**: Cache pip dependencies
2. **Parallel jobs**: Run independent jobs in parallel
3. **Conditional steps**: Skip unnecessary steps
4. **Matrix builds**: Test multiple Python versions (optional)

---

## 🔗 Related Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [Apache Airflow Testing](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html#testing-a-dag)
- [Docker Build Action](https://github.com/docker/build-push-action)

---

## 📄 Workflow Files

```
.github/workflows/
├── ci.yml                  # Main CI/CD pipeline
└── docker-build.yml        # Docker image build & validation
```

---

**Status**: ✅ Both workflows configured and ready to use!
