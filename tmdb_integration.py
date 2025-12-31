"""Integration with The Movie Database (TMDB) API."""
import requests
from flask import current_app


class TMDBClient:
    """Client for interacting with TMDB API."""
    
    def __init__(self):
        self.api_key = None
        self.base_url = None
    
    def _get_config(self):
        """Get configuration from Flask app context."""
        if not self.api_key:
            self.api_key = current_app.config.get('TMDB_API_KEY')
        if not self.base_url:
            self.base_url = current_app.config.get('TMDB_BASE_URL')
    
    def search_movie(self, title, year=None):
        """
        Search for a movie by title.
        
        Args:
            title: Movie title to search for
            year: Optional year to narrow search
            
        Returns:
            Dictionary with search results or None if error
        """
        self._get_config()
        
        if not self.api_key:
            print("TMDB API key not configured")
            return None
        
        url = f"{self.base_url}/search/movie"
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'accept': 'application/json'
        }
        params = {
            'query': title
        }
        
        if year:
            params['year'] = year
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error searching TMDB: {e}")
            return None
    
    def get_movie_details(self, tmdb_id):
        """
        Get detailed information about a movie.
        
        Args:
            tmdb_id: TMDB movie ID
            
        Returns:
            Dictionary with movie details or None if error
        """
        self._get_config()
        
        if not self.api_key:
            print("TMDB API key not configured")
            return None
        
        url = f"{self.base_url}/movie/{tmdb_id}"
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'accept': 'application/json'
        }
        params = {
            'append_to_response': 'credits,videos'
        }
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching movie details from TMDB: {e}")
            return None
    
    def get_movie_poster_url(self, poster_path, size='w500'):
        """
        Get full URL for a movie poster.
        
        Args:
            poster_path: Poster path from TMDB API
            size: Image size (w92, w154, w185, w342, w500, w780, original)
            
        Returns:
            Full URL to poster image
        """
        if not poster_path:
            return None
        
        return f"https://image.tmdb.org/t/p/{size}{poster_path}"


# Stub functions for future implementation
def enrich_movie_data(movie_title):
    """
    Stub: Fetch and return enriched movie data from TMDB.
    
    Args:
        movie_title: Title of the movie to enrich
        
    Returns:
        Dictionary with movie data or None
    """
    client = TMDBClient()
    search_results = client.search_movie(movie_title)
    
    if not search_results or not search_results.get('results'):
        return None
    
    # Get the first result (most relevant)
    movie = search_results['results'][0]
    tmdb_id = movie.get('id')
    
    # Get detailed information
    details = client.get_movie_details(tmdb_id)
    
    if details:
        return {
            'tmdb_id': tmdb_id,
            'title': details.get('title'),
            'overview': details.get('overview'),
            'release_date': details.get('release_date'),
            'poster_url': client.get_movie_poster_url(details.get('poster_path')),
            'backdrop_url': client.get_movie_poster_url(details.get('backdrop_path'), 'original'),
            'vote_average': details.get('vote_average'),
            'runtime': details.get('runtime'),
            'genres': [g['name'] for g in details.get('genres', [])],
        }
    
    return None
