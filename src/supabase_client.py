import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class SupabaseClient:
    def __init__(self, supabase_url=None, supabase_key=None):
        self.url = supabase_url or os.getenv("SUPABASE_URL")
        self.key = supabase_key or os.getenv("SUPABASE_KEY")

        if not self.url or not self.key:
            raise ValueError("Supabase URL and Key must be provided or set as environment variables.")
        
        self.client: Client = create_client(self.url, self.key)

    def upsert_movies(self, movies_data, table_name="movies"):
        """
        Upserts movie data into a Supabase table.
        'upsert' will insert new rows or update existing ones if a conflict on the primary key occurs.
        
        Args:
            movies_data (list): A list of dictionaries, where each dictionary represents a movie.
            table_name (str): The name of the table to upsert data into.
        
        Returns:
            The response from the Supabase client.
        """
        if not movies_data:
            print("No movie data to upsert.")
            return None
        
        try:
            # The 'upsert' method is suitable for this use case.
            # We assume the 'id' from TMDB is the primary key in our Supabase table.
            response = self.client.table(table_name).upsert(movies_data).execute()
            return response
        except Exception as e:
            print(f"An error occurred while upserting data to Supabase: {e}")
            return None

if __name__ == '__main__':
    # Example Usage:
    # Make sure you have a .env file with SUPABASE_URL and SUPABASE_KEY.
    
    # This example requires a 'movies' table in your Supabase project
    # with at least 'id' and 'title' columns. 'id' should be the primary key.
    
    try:
        supabase_handler = SupabaseClient()
        
        # Example movie data
        sample_movies = [
            {'id': 999999, 'title': 'Test Movie 1', 'overview': 'This is a test.'},
            {'id': 1000000, 'title': 'Test Movie 2', 'overview': 'Another test.'}
        ]
        
        print(f"Attempting to upsert {len(sample_movies)} movies to the 'movies' table...")
        
        api_response = supabase_handler.upsert_movies(sample_movies)
        
        if api_response:
            print("Successfully upserted data to Supabase.")
            # You can inspect the response data if needed
            # print(api_response.data)
        else:
            print("Failed to upsert data.")
            
    except ValueError as e:
        print(e) 