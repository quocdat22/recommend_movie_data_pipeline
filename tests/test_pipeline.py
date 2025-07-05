import pytest
from unittest.mock import MagicMock
from src.pipeline import DataPipeline

@pytest.fixture
def mock_tmdb_client(mocker):
    """Fixture to mock TMDBClient."""
    client = MagicMock()
    # Sample data for one movie page
    client.get_top_rated_movies.return_value = {
        'results': [
            {'id': 1, 'title': 'Movie 1', 'genre_ids': [28, 12]},
        ]
    }
    # Sample keywords
    client.get_movie_keywords.return_value = {
        'keywords': [{'name': 'action'}, {'name': 'adventure'}]
    }
    # Sample credits with more than 3 cast members to test slicing
    client.get_movie_credits.return_value = {
        'cast': [
            {'name': 'Actor A', 'order': 0},
            {'name': 'Actor B', 'order': 1},
            {'name': 'Actor C', 'order': 2},
            {'name': 'Actor D', 'order': 3},
        ]
    }
    return client

@pytest.fixture
def mock_supabase_client(mocker):
    """Fixture to mock SupabaseClient."""
    client = MagicMock()
    client.upsert_movies.return_value = None # We don't care about the return value for this test
    return client

@pytest.fixture
def pipeline_instance(mocker, mock_tmdb_client, mock_supabase_client):
    """Fixture to create a DataPipeline instance with mocked clients."""
    mocker.patch('src.pipeline.TMDBClient', return_value=mock_tmdb_client)
    mocker.patch('src.pipeline.SupabaseClient', return_value=mock_supabase_client)
    return DataPipeline()

def test_enrich_movie_logic(pipeline_instance):
    """
    Test the internal logic of _enrich_movie to ensure it processes data correctly.
    """
    sample_movie = {'id': 1, 'title': 'Test Movie', 'genre_ids': [18]}
    
    enriched_movie = pipeline_instance._enrich_movie(sample_movie)

    assert enriched_movie is not None
    assert enriched_movie['id'] == 1
    assert enriched_movie['title'] == 'Test Movie'
    
    # Check if keywords are correctly extracted
    assert 'keywords' in enriched_movie
    assert enriched_movie['keywords'] == ['action', 'adventure']

    # Check if top 3 cast members are correctly extracted and ordered
    assert 'top_cast' in enriched_movie
    assert len(enriched_movie['top_cast']) == 3
    assert enriched_movie['top_cast'] == ['Actor A', 'Actor B', 'Actor C']

@pytest.mark.parametrize(
    "pipeline_type, fetcher_method_name",
    [
        ('top_rated', 'get_top_rated_movies'),
        ('popular', 'get_popular_movies')
    ]
)
def test_run_pipeline_flow(pipeline_instance, mock_tmdb_client, mock_supabase_client, pipeline_type, fetcher_method_name):
    """
    Test the main 'run' method to ensure it calls the correct client method based on pipeline_type.
    """
    test_pages = 2
    pipeline_instance.run(pipeline_type=pipeline_type, total_pages=test_pages)

    # Get the correct mock fetcher method from the client
    fetcher_method = getattr(mock_tmdb_client, fetcher_method_name)

    # Verify that the correct fetcher method was called for each page
    assert fetcher_method.call_count == test_pages
    
    # Verify that the enrichment and storage methods were also called
    assert mock_tmdb_client.get_movie_keywords.call_count == test_pages
    assert mock_tmdb_client.get_movie_credits.call_count == test_pages
    assert mock_supabase_client.upsert_movies.call_count == test_pages
    
    # Check that the other fetcher was NOT called
    other_method_name = 'get_popular_movies' if pipeline_type == 'top_rated' else 'get_top_rated_movies'
    other_method = getattr(mock_tmdb_client, other_method_name)
    assert other_method.call_count == 0

def test_run_invalid_pipeline_type(pipeline_instance):
    """
    Test that running with an invalid pipeline_type raises a ValueError.
    """
    with pytest.raises(ValueError, match="Invalid pipeline_type"):
        pipeline_instance.run(pipeline_type='invalid_type', total_pages=1) 