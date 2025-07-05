import pytest
from unittest.mock import MagicMock
from src.tmdb_client import TMDBClient
import os

@pytest.fixture
def mock_requests_get(mocker):
    """Fixture to mock requests.get."""
    return mocker.patch('requests.get')

@pytest.fixture
def tmdb_client():
    """Fixture to create a TMDBClient instance with a dummy API key."""
    return TMDBClient(api_key="dummy_api_key")

def test_get_top_rated_movies(tmdb_client, mock_requests_get):
    """
    Test that get_top_rated_movies calls the correct endpoint with correct params.
    """
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"results": ["movie1", "movie2"]}
    mock_requests_get.return_value = mock_response

    page = 5
    tmdb_client.get_top_rated_movies(page=page)

    expected_url = f"{tmdb_client.base_url}/movie/top_rated"
    expected_params = {'page': page, 'api_key': tmdb_client.api_key}

    mock_requests_get.assert_called_once_with(expected_url, params=expected_params)

def test_get_popular_movies(tmdb_client, mock_requests_get):
    """
    Test that get_popular_movies calls the correct endpoint with correct params.
    """
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"results": ["movie1", "movie2"]}
    mock_requests_get.return_value = mock_response

    page = 3
    tmdb_client.get_popular_movies(page=page)

    expected_url = f"{tmdb_client.base_url}/movie/popular"
    expected_params = {'page': page, 'api_key': tmdb_client.api_key}

    mock_requests_get.assert_called_once_with(expected_url, params=expected_params)

def test_get_movie_keywords(tmdb_client, mock_requests_get):
    """
    Test that get_movie_keywords calls the correct endpoint.
    """
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"keywords": ["keyword1"]}
    mock_requests_get.return_value = mock_response

    movie_id = 123
    tmdb_client.get_movie_keywords(movie_id)

    expected_url = f"{tmdb_client.base_url}/movie/{movie_id}/keywords"
    expected_params = {'api_key': tmdb_client.api_key}
    
    mock_requests_get.assert_called_once_with(expected_url, params=expected_params)

def test_get_movie_credits(tmdb_client, mock_requests_get):
    """
    Test that get_movie_credits calls the correct endpoint.
    """
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"cast": ["actor1"]}
    mock_requests_get.return_value = mock_response

    movie_id = 456
    tmdb_client.get_movie_credits(movie_id)

    expected_url = f"{tmdb_client.base_url}/movie/{movie_id}/credits"
    expected_params = {'api_key': tmdb_client.api_key}
    
    mock_requests_get.assert_called_once_with(expected_url, params=expected_params)

def test_api_key_error(mocker):
    """
    Test that a ValueError is raised if the API key is not provided and
    the environment variable is also not set.
    """
    # Mock os.getenv to ensure it returns None for this test
    mocker.patch('os.getenv', return_value=None)
    
    with pytest.raises(ValueError, match="TMDB_API_KEY is not set"):
        # Explicitly pass None to override any potential env var
        TMDBClient(api_key=None) 