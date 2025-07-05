from setuptools import setup, find_packages

setup(
    name='movie_data_pipeline',
    version='0.1.0',
    packages=find_packages(),
    description='A data pipeline for fetching movie data.',
    install_requires=[
        "apache-airflow>=2.8.0",
        "apache-airflow-providers-http",
        "requests",
        "python-dotenv",
        "supabase",
        "pendulum",  # pendulum is used for dates in the DAG
    ]
) 