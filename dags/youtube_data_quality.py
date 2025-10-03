"""
🔍 YouTube Data Quality DAG - Simple Quality Checks
===================================================
Run Soda Core quality checks and save reports.
"""

from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

default_args = {
    'owner': 'airflow',
    'retries': 0,
}

with DAG(
    dag_id='data_quality',
    default_args=default_args,
    description='YouTube data quality validation',
    schedule=None,
    start_date=datetime(2025, 10, 1),
    catchup=False,
    tags=['youtube', 'quality'],
) as dag:
    
    run_soda_scan = BashOperator(
        task_id='run_soda_scan',
        bash_command="""
        # Database connection
        export POSTGRES_HOST=postgres
        export POSTGRES_PORT=5432
        export POSTGRES_USER=postgres
        export POSTGRES_PASSWORD=postgres
        export POSTGRES_DB=youtube_dwh
        
        cd /usr/local/airflow
        
        # Create timestamp for report
        TIMESTAMP=$(date +%Y%m%d_%H%M%S)
        REPORT_FILE="/usr/local/airflow/include/soda/reports/quality_report_${TIMESTAMP}.json"
        
        echo "🔍 Running Soda quality checks..."
        echo "📊 Report will be saved to: $REPORT_FILE"
        
        # Run Soda scan with report output
        soda scan \
            -d postgres_dwh \
            -c include/soda/configuration.yml \
            include/soda/checks/videos_quality.yml \
            > "$REPORT_FILE"
        
        RESULT=$?
        
        # Show report location
        echo ""
        echo "✅ Quality check complete!"
        echo "📄 Report saved: $REPORT_FILE"
        
        exit $RESULT
        """,
    )
