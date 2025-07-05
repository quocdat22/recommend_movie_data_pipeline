from __future__ import annotations
import pendulum

from airflow.models.dag import DAG
from airflow.operators.python import PythonOperator

# Since the 'src' package is now installed directly into the Airflow environment
# via the Dockerfile, we can import it directly at the top level.
from src.pipeline import DataPipeline

def run_pipeline_task(**kwargs):
    """
    This task now directly calls the DataPipeline.
    Credentials are pulled from the kwargs passed by the operator.
    """
    # Airflow will pass the templated op_kwargs to this function's kwargs
    tmdb_api_key = kwargs["tmdb_api_key"]
    supabase_url = kwargs["supabase_url"]
    supabase_key = kwargs["supabase_key"]

    print("Executing pipeline directly inside the main Airflow environment...")
    pipeline = DataPipeline(
        tmdb_api_key=tmdb_api_key,
        supabase_url=supabase_url,
        supabase_key=supabase_key
    )
    pipeline.run(pipeline_type='popular', total_pages=2)
    print("Pipeline execution finished.")

with DAG(
    dag_id="daily_fetch_popular_movies",
    start_date=pendulum.datetime(2023, 1, 1, tz="UTC"),
    schedule="@daily",
    catchup=False,
    tags=["movies", "data-pipeline"],
    doc_md="""
    ## Daily Fetch Popular Movies DAG
    This DAG runs the movie data pipeline directly using the PythonOperator.
    The environment is pre-built by Docker, ensuring all dependencies are available.
    """,
    render_template_as_native_obj=True,
) as dag:
    
    run_pipeline = PythonOperator(
        task_id="run_pipeline",
        python_callable=run_pipeline_task,
        # op_kwargs are templated at runtime and passed to the python_callable
        op_kwargs={
            "tmdb_api_key": "{{ conn.tmdb_default.password }}",
            "supabase_url": "{{ conn.supabase_default.host }}",
            "supabase_key": "{{ conn.supabase_default.password }}",
        },
    ) 