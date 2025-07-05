import os
import requests
from dotenv import load_dotenv

load_dotenv()

class TMDBClient:
    def __init__(self, api_key=None):
        # The API key is now expected to be provided directly or via an environment variable.
        self.api_key = api_key or os.getenv("TMDB_API_KEY")

        if not self.api_key:
            raise ValueError("TMDB_API_KEY is not set. Please provide it or set it as an environment variable.")
        
        self.base_url = "https://api.themoviedb.org/3"

    def _make_request(self, endpoint, params=None):
        """Helper function to make requests to the TMDB API."""
        if params is None:
            params = {}
        
        # Add the API key to every request
        params['api_key'] = self.api_key
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return None

    def get_movies_by_year(self, year, page=1):
        """Fetch movies for a specific year."""
        endpoint = "/discover/movie"
        params = {
            'primary_release_year': year,
            'sort_by': 'popularity.desc',
            'page': page
        }
        return self._make_request(endpoint, params)

    def get_top_rated_movies(self, page=1):
        """Fetch a page of top-rated movies."""
        endpoint = "/movie/top_rated"
        params = {
            'page': page
        }
        return self._make_request(endpoint, params)

    def get_popular_movies(self, page=1):
        """Fetch a page of popular movies."""
        endpoint = "/movie/popular"
        params = {
            'page': page
        }
        return self._make_request(endpoint, params)

    def get_movie_keywords(self, movie_id):
        """Fetch keywords associated with a movie."""
        endpoint = f"/movie/{movie_id}/keywords"
        return self._make_request(endpoint)

    def get_movie_credits(self, movie_id):
        """Fetch cast/crew credits for a movie."""
        endpoint = f"/movie/{movie_id}/credits"
        return self._make_request(endpoint)

if __name__ == '__main__':
    # Example usage:
    # Ensure you have a .env file with TMDB_API_KEY set
    
    client = TMDBClient()
    
    # Fetch movies from the year 2023
    movies_data = client.get_movies_by_year(2023)
    
    if movies_data and 'results' in movies_data:
        print(f"Successfully fetched {len(movies_data['results'])} movies from 2023.")
        # Print the first 5 movies
        for movie in movies_data['results'][:5]:
            print(f"- {movie['title']} (ID: {movie['id']})")
    else:
        print("Failed to fetch movies.") 