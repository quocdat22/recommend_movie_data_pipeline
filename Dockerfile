# Start from the official Airflow image for version 2.9.2
FROM apache/airflow:2.9.2

# Set the ARG for DEBIAN_FRONTEND to avoid interactive prompts during package installation.
ARG DEBIAN_FRONTEND=noninteractive

# Set the Airflow user. This is important for permissions.
ARG AIRFLOW_UID=50000
USER root
RUN usermod -u ${AIRFLOW_UID} airflow && usermod -g 0 airflow

# Switch to the airflow user before installing packages
USER airflow

# Copy the requirements file first and install, to leverage Docker layer caching
COPY airflow/requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

# Copy the entire project structure
COPY . /opt/airflow

# Set the working directory
WORKDIR /opt/airflow

# Install the local project in editable mode so that 'src' is importable
RUN pip install -e .

# Copy the project source code (for the pipeline) and the dags folder
COPY src /opt/airflow/src
COPY airflow/dags /opt/airflow/dags

# Make start script executable
USER root
RUN chmod +x /opt/airflow/start.sh

# Switch back to the airflow user
USER airflow 

# Set the default command to run our start script
CMD ["/opt/airflow/start.sh"] 