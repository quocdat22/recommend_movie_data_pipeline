from .tmdb_client import TMDBClient
from .supabase_client import SupabaseClient
import time
import argparse

class DataPipeline:
    def __init__(self, tmdb_api_key=None, supabase_url=None, supabase_key=None):
        self.tmdb_client = TMDBClient(api_key=tmdb_api_key)
        self.supabase_client = SupabaseClient(supabase_url=supabase_url, supabase_key=supabase_key)

    def _enrich_movie(self, movie):
        """Fetch keywords and top-3 cast names for a single movie and return a processed dict."""
        movie_id = movie.get('id')
        if not movie_id:
            return None

        # Fetch keywords
        keywords_resp = self.tmdb_client.get_movie_keywords(movie_id)
        keyword_names = []
        if keywords_resp and keywords_resp.get('keywords'):
            keyword_names = [kw['name'] for kw in keywords_resp['keywords']]

        # Fetch credits (cast)
        credits_resp = self.tmdb_client.get_movie_credits(movie_id)
        cast_names = []
        if credits_resp and credits_resp.get('cast'):
            sorted_cast = sorted(credits_resp['cast'], key=lambda x: x.get('order', 999))
            cast_names = [member['name'] for member in sorted_cast[:3]]

        processed_movie = {
            'id': movie_id,
            'title': movie.get('title'),
            'overview': movie.get('overview'),
            'release_date': movie.get('release_date'),
            'popularity': movie.get('popularity'),
            'vote_average': movie.get('vote_average'),
            'vote_count': movie.get('vote_count'),
            'poster_path': movie.get('poster_path'),
            'genre_ids': movie.get('genre_ids'),
            'keywords': keyword_names,
            'top_cast': cast_names
        }

        # Ensure required fields
        if processed_movie['title']:
            return processed_movie
        return None

    def run(self, pipeline_type: str = 'top_rated', total_pages: int = 400):
        """
        Runs the full ETL pipeline for a specified type ('top_rated' or 'popular').
        """
        print(f"Starting data pipeline for '{pipeline_type}' movies across {total_pages} pages")

        fetcher_method_map = {
            'top_rated': self.tmdb_client.get_top_rated_movies,
            'popular': self.tmdb_client.get_popular_movies
        }

        fetcher_method = fetcher_method_map.get(pipeline_type)
        if not fetcher_method:
            raise ValueError(f"Invalid pipeline_type: '{pipeline_type}'. Must be 'top_rated' or 'popular'.")

        for page in range(1, total_pages + 1):
            print(f"Fetching page {page} of {pipeline_type} movies…")
            movies_data = fetcher_method(page=page)

            if not movies_data or not movies_data.get('results'):
                print("  -> No results returned. Stopping early.")
                break

            processed_batch = []
            for movie in movies_data['results']:
                enriched = self._enrich_movie(movie)
                if enriched:
                    processed_batch.append(enriched)

                # Brief sleep between extra API calls to respect rate limits
                time.sleep(0.25)

            if processed_batch:
                print(f"  -> Upserting {len(processed_batch)} movies to Supabase…")
                self.supabase_client.upsert_movies(processed_batch)
            else:
                print("  -> No valid movies on this page.")

            # Sleep between pages to avoid hitting rate limits
            time.sleep(0.5)

        print("Data pipeline finished.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run the movie data pipeline.")
    parser.add_argument(
        '--type', 
        type=str, 
        default='top_rated', 
        choices=['top_rated', 'popular'],
        help="The type of pipeline to run ('top_rated' or 'popular')."
    )
    parser.add_argument(
        '--pages', 
        type=int, 
        default=2, 
        help="The number of pages to fetch."
    )

    args = parser.parse_args()

    pipeline = DataPipeline()
    pipeline.run(pipeline_type=args.type, total_pages=args.pages) 