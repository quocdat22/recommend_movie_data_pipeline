# Movie Data Pipeline

This module is responsible for extracting, transforming, and loading (ETL) movie data from [TheMovieDB API](https://www.themoviedb.org/) into a Supabase database.

The pipeline is designed to be scheduled and managed by Apache Airflow.

## 🚀 Getting Started

### 1. Prerequisites

- Python 3.9+
- An account with [TheMovieDB](https://www.themoviedb.org/signup) to get an API key.
- A [Supabase](https://supabase.com/) project.

### 2. Installation

1.  **Clone the repository (if it's a separate repo):**

    ```bash
    git clone <repository-url>
    cd movie-data-pipeline
    ```

2.  **Create and activate a virtual environment:**

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

### 3. Configuration

1.  Create a `.env` file in the root of this module.
2.  Add your credentials to the `.env` file:

    ```env
    TMDB_API_KEY="your_tmdb_api_key"
    SUPABASE_URL="your_supabase_project_url"
    SUPABASE_KEY="your_supabase_api_key"
    ```

## Usage

The pipeline can fetch both **Top Rated** and **Popular** movies. The data for each movie is enriched with its associated keywords and top 3 cast members.

### Running the Pipeline

You can run the pipeline from the command line inside the `movie-data-pipeline` directory. Use the `--type` and `--pages` flags to control the execution.

**Examples:**

```bash
# Fetch the first 2 pages of POPULAR movies (for testing)
python -m src.pipeline --type popular --pages 2

# Fetch the first 5 pages of TOP RATED movies
python -m src.pipeline --type top_rated --pages 5

# Fetch all 400 pages of TOP RATED movies (production run)
python -m src.pipeline --type top_rated --pages 400
```

## 🗄️ Supabase Table Schema

Truy cập **SQL Editor → New Query** trong dashboard Supabase và chạy lệnh sau để tạo bảng lưu trữ dữ liệu phim (nếu bảng chưa tồn tại):

```sql
create table if not exists public.movies (
    id integer primary key,
    title text not null,
    overview text,
    release_date date,
    popularity numeric,
    vote_average numeric,
    vote_count integer,
    poster_path text,
    genre_ids integer[],            -- danh sách genre id theo TMDB
    keywords text[],                -- tất cả keyword name liên quan
    top_cast text[]                 -- tên 3 diễn viên đầu tiên
);
```

> 📌  Lưu ý: `text[]` và `integer[]` là kiểu mảng của PostgreSQL nên Supabase hỗ trợ trực tiếp.

## 🌬️ Airflow Integration for Production

This pipeline is designed to be automated with a production-ready Apache Airflow setup using Docker Compose. This method runs each Airflow component as a separate, isolated service, which is the standard for production environments.

### 1. Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/) must be installed on your system.

### 2. Environment Configuration

The Docker Compose setup uses a `.env` file to manage environment-specific variables, primarily for setting file permissions correctly between your host machine and the Docker containers.

1.  **Create the `.env` file**:
    The following command creates the `.env` file and automatically populates it with your current user ID. This ensures that files written by Airflow containers (like logs) are owned by you.
    ```bash
    echo "AIRFLOW_UID=$(id -u)" > .env
    ```

### 3. Running Airflow with Docker Compose

1.  **Build and Start All Services**:
    Navigate to the `movie-data-pipeline` directory and run the following command:
    ```bash
    docker-compose up --build -d
    ```
    - `--build`: This flag tells Docker Compose to build the custom Airflow image from the `Dockerfile`. You only need to use this on the first run or whenever you modify the `Dockerfile` or `requirements.txt`.
    - `-d`: Runs the containers in detached mode (in the background).

2.  **What Happens on First Run?**:
    - Docker Compose builds the `airflow-movie-pipeline` image.
    - The `postgres` container starts.
    - The `airflow-init` container runs once to initialize the database and create a default user with credentials **admin / admin**.
    - The `airflow-webserver`, `airflow-scheduler`, and `airflow-triggerer` services start.

3.  **Accessing the Airflow UI**:
    You can now access the Airflow UI at **[http://localhost:8080](http://localhost:8080)**. Log in with `admin` / `admin`.

### 4. Configure Airflow Connections

For the DAG to run successfully, you must configure the necessary credentials in the Airflow UI. This is a secure alternative to hardcoding secrets.

Navigate to **Admin -> Connections** in the Airflow UI and add the following two connections:

#### TMDB Connection
- **Connection Id**: `tmdb_default`
- **Connection Type**: `HTTP`
- **Password**: Your TheMovieDB API key.

#### Supabase Connection
- **Connection Id**: `supabase_default`
- **Connection Type**: `Generic`
- **Host**: Your Supabase project URL (e.g., `https://xxxx.supabase.co`).
- **Password**: Your Supabase `service_role` key (Note: For production, it's safer to use the service role key).

### 5. Managing the Environment

- **To view logs**:
  ```bash
  # View all logs
  docker-compose logs -f

  # View logs for a specific service (e.g., scheduler)
  docker-compose logs -f airflow-scheduler
  ```

- **To stop the environment**:
  ```bash
  docker-compose down
  ```

- **To stop and remove data volumes** (use with caution):
  ```bash
  docker-compose down --volumes
  ```

## GitHub Actions Workflow

This project includes a GitHub Actions workflow that allows you to manually trigger Airflow DAGs remotely. This is especially useful when you've deployed your Airflow instance to a server with public access.

### Setup for GitHub Actions

1. In your GitHub repository, go to **Settings** > **Secrets and variables** > **Actions**

2. Add the following secrets:
   - `AIRFLOW_USERNAME`: Your Airflow username (default is "admin")
   - `AIRFLOW_PASSWORD`: Your Airflow password
   - `TMDB_API_KEY`: Your TMDB API key
   - `SUPABASE_URL`: Your Supabase URL
   - `SUPABASE_KEY`: Your Supabase API key

### Triggering a DAG Manually

1. Go to the **Actions** tab in your GitHub repository
2. Select the "Trigger Airflow DAG" workflow
3. Click on **Run workflow**
4. Fill in the required parameters:
   - **DAG ID**: The ID of the DAG you want to trigger (default: `daily_fetch_popular_movies`)
   - **Airflow API URL**: The URL where your Airflow API is accessible (e.g., `https://your-airflow-instance.com`)
   - **Total pages**: Number of pages to fetch from TMDB API (default: 2)
   - **Optional JSON configuration**: Additional configuration parameters in JSON format

5. Click **Run workflow** to trigger the DAG

### How It Works

The workflow:
1. Uses the Airflow REST API to trigger a DAG run
2. Passes configuration parameters to the DAG
3. Automatically includes your credentials from GitHub Secrets
4. Provides feedback on the success or failure of the trigger operation

This allows you to run your data pipeline on-demand without needing direct access to the Airflow server.
