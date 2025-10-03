"""
🧪 DAG Validation Tests
Simple tests to validate DAG file structure (without importing Airflow)

Test Count: 6 DAG tests
"""

import pytest
from pathlib import Path


# ==========================================
# ✅ Test 9-14: DAG File Existence and Structure
# ==========================================

@pytest.mark.dag
def test_produce_json_dag_exists():
    """Test 9: produce_JSON DAG file exists"""
    dag_file = Path("dags/youtube_extract.py")
    assert dag_file.exists(), "produce_JSON DAG file not found"


@pytest.mark.dag
def test_update_db_dag_exists():
    """Test 10: update_db DAG file exists"""
    dag_file = Path("dags/youtube_load_db.py")
    assert dag_file.exists(), "update_db DAG file not found"


@pytest.mark.dag
def test_data_quality_dag_exists():
    """Test 11: data_quality DAG file exists"""
    dag_file = Path("dags/youtube_data_quality.py")
    assert dag_file.exists(), "data_quality DAG file not found"


@pytest.mark.dag
def test_produce_json_has_dag_id():
    """Test 12: produce_JSON file contains dag_id definition"""
    dag_file = Path("dags/youtube_extract.py")
    content = dag_file.read_text(encoding='utf-8')
    
    assert 'dag_id' in content, "No dag_id found in produce_JSON"
    assert 'produce_JSON' in content, "DAG ID 'produce_JSON' not found"


@pytest.mark.dag
def test_update_db_has_dag_id():
    """Test 13: update_db file contains dag_id definition"""
    dag_file = Path("dags/youtube_load_db.py")
    content = dag_file.read_text(encoding='utf-8')
    
    assert 'dag_id' in content, "No dag_id found in update_db"
    assert 'update_db' in content, "DAG ID 'update_db' not found"


@pytest.mark.dag
def test_data_quality_has_dag_id():
    """Test 14: data_quality file contains dag_id definition"""
    dag_file = Path("dags/youtube_data_quality.py")
    content = dag_file.read_text(encoding='utf-8')
    
    assert 'dag_id' in content, "No dag_id found in data_quality"
    assert 'data_quality' in content, "DAG ID 'data_quality' not found"


# ==========================================
# ✅ Test 15-18: Task Validation
# ==========================================

@pytest.mark.dag
def test_produce_json_has_extract_task():
    """Test 15: produce_JSON has extract_youtube_videos task"""
    dag_file = Path("dags/youtube_extract.py")
    content = dag_file.read_text(encoding='utf-8')
    
    assert 'task_id="extract_youtube_videos"' in content or "task_id='extract_youtube_videos'" in content


@pytest.mark.dag
def test_update_db_has_all_tasks():
    """Test 16: update_db has all 4 required tasks"""
    dag_file = Path("dags/youtube_load_db.py")
    content = dag_file.read_text(encoding='utf-8')
    
    required_tasks = ['find_latest_json', 'sync_to_staging', 'transform_to_core', 'trigger_data_quality']
    for task in required_tasks:
        assert task in content, f"Task {task} not found in update_db"


@pytest.mark.dag
def test_data_quality_has_soda_task():
    """Test 17: data_quality has run_soda_scan task"""
    dag_file = Path("dags/youtube_data_quality.py")
    content = dag_file.read_text(encoding='utf-8')
    
    assert 'run_soda_scan' in content or 'run_soda' in content


# ==========================================
# ✅ Test 19-20: Orchestration Validation
# ==========================================

@pytest.mark.dag
def test_produce_json_triggers_update_db():
    """Test 18: produce_JSON triggers update_db DAG"""
    dag_file = Path("dags/youtube_extract.py")
    content = dag_file.read_text(encoding='utf-8')
    
    assert 'TriggerDagRunOperator' in content
    assert 'trigger_dag_id="update_db"' in content or "trigger_dag_id='update_db'" in content


@pytest.mark.dag
def test_update_db_triggers_data_quality():
    """Test 19: update_db triggers data_quality DAG"""
    dag_file = Path("dags/youtube_load_db.py")
    content = dag_file.read_text(encoding='utf-8')
    
    assert 'TriggerDagRunOperator' in content
    assert 'trigger_dag_id="data_quality"' in content or "trigger_dag_id='data_quality'" in content


@pytest.mark.dag
def test_complete_pipeline_orchestration():
    """Test 20: Complete pipeline orchestration chain exists"""
    # Check produce_JSON → update_db
    extract_file = Path("dags/youtube_extract.py").read_text(encoding='utf-8')
    assert 'update_db' in extract_file
    
    # Check update_db → data_quality
    load_file = Path("dags/youtube_load_db.py").read_text(encoding='utf-8')
    assert 'data_quality' in load_file


# ==========================================
# 📊 Test Summary
# ==========================================
"""
✅ DAG VALIDATION TESTS SUMMARY (12 tests):

File Existence:
9.  test_produce_json_dag_exists
10. test_update_db_dag_exists
11. test_data_quality_dag_exists

DAG ID Validation:
12. test_produce_json_has_dag_id
13. test_update_db_has_dag_id
14. test_data_quality_has_dag_id

Task Validation:
15. test_produce_json_has_extract_task
16. test_update_db_has_all_tasks
17. test_data_quality_has_soda_task

Orchestration:
18. test_produce_json_triggers_update_db
19. test_update_db_triggers_data_quality
20. test_complete_pipeline_orchestration

Total: 20/20 tests complete ✅
"""
