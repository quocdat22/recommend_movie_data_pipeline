# Start from the official Airflow image for version 2.9.2
FROM apache/airflow:2.9.2

# Set the ARG for DEBIAN_FRONTEND to avoid interactive prompts during package installation.
ARG DEBIAN_FRONTEND=noninteractive

# Set the Airflow user. This is important for permissions.
ARG AIRFLOW_UID=50000
USER root
RUN usermod -u ${AIRFLOW_UID} airflow && usermod -g 0 airflow

# Create start script
RUN echo '#!/bin/bash' > /opt/airflow/start.sh && \
    echo 'set -e' >> /opt/airflow/start.sh && \
    echo '' >> /opt/airflow/start.sh && \
    echo '# Wait for PostgreSQL to be ready' >> /opt/airflow/start.sh && \
    echo 'echo "Waiting for PostgreSQL to be ready..."' >> /opt/airflow/start.sh && \
    echo 'sleep 10' >> /opt/airflow/start.sh && \
    echo '' >> /opt/airflow/start.sh && \
    echo '# Initialize the database if it hasn'"'"'t been initialized yet' >> /opt/airflow/start.sh && \
    echo 'airflow db init' >> /opt/airflow/start.sh && \
    echo '' >> /opt/airflow/start.sh && \
    echo '# Create admin user if it doesn'"'"'t exist' >> /opt/airflow/start.sh && \
    echo 'airflow users list | grep -q $AIRFLOW_ADMIN_USERNAME || \\' >> /opt/airflow/start.sh && \
    echo '  airflow users create \\' >> /opt/airflow/start.sh && \
    echo '    --username $AIRFLOW_ADMIN_USERNAME \\' >> /opt/airflow/start.sh && \
    echo '    --password $AIRFLOW_ADMIN_PASSWORD \\' >> /opt/airflow/start.sh && \
    echo '    --firstname Admin \\' >> /opt/airflow/start.sh && \
    echo '    --lastname User \\' >> /opt/airflow/start.sh && \
    echo '    --role Admin \\' >> /opt/airflow/start.sh && \
    echo '    --email $AIRFLOW_ADMIN_EMAIL' >> /opt/airflow/start.sh && \
    echo '' >> /opt/airflow/start.sh && \
    echo '# Start the webserver' >> /opt/airflow/start.sh && \
    echo 'exec airflow webserver' >> /opt/airflow/start.sh && \
    chmod +x /opt/airflow/start.sh

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

# Switch back to the airflow user
USER airflow 

# Set the default command to run our start script
CMD ["/opt/airflow/start.sh"] 