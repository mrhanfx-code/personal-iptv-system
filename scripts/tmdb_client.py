"""
TMDB API Integration Module
Handles metadata retrieval, poster downloads, and caching for IPTV playlists
"""

import os
import sqlite3
import requests
from typing import Optional, Dict, Any, List
from PIL import Image
import io
from fuzzywuzzy import fuzz
from queue import PriorityQueue
import time


class TMDBClient:
    """TMDB API v3 wrapper with caching and rate limiting"""
    
    def __init__(self, api_key: str, config: Dict[str, Any]):
        self.api_key = api_key
        self.base_url = "https://api.themoviedb.org/3"
        self.config = config
        self.request_queue = PriorityQueue()
        self.session = requests.Session()
        self._init_cache()
        
    def _init_cache(self):
        """Initialize SQLite cache database"""
        cache_dir = self.config['paths']['cache_dir']
        os.makedirs(cache_dir, exist_ok=True)
        
        db_path = os.path.join(cache_dir, 'metadata.db')
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS metadata_cache (
                title TEXT PRIMARY KEY,
                tmdb_id INTEGER,
                poster_url TEXT,
                backdrop_url TEXT,
                cast TEXT,
                rating REAL,
                synopsis TEXT,
                genres TEXT,
                year INTEGER,
                cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()
        
    def normalize_title(self, title: str) -> str:
        """Normalize title for TMDB matching"""
        # Remove file extensions
        title = os.path.splitext(title)[0]
        # Clean common patterns
        title = title.replace('_', ' ')
        title = title.replace('.', ' ')
        # Remove extra whitespace
        title = ' '.join(title.split())
        return title.strip()
    
    def fuzzy_match(self, title: str, candidates: List[str], threshold: float = 0.75) -> Optional[str]:
        """Find best match using fuzzy string matching"""
        normalized = self.normalize_title(title)
        best_match = None
        best_score = 0
        
        for candidate in candidates:
            score = fuzz.ratio(normalized.lower(), candidate.lower()) / 100
            if score > best_score and score >= threshold:
                best_score = score
                best_match = candidate
                
        return best_match
    
    def search_movie(self, title: str) -> Optional[Dict[str, Any]]:
        """Search TMDB for movie by title"""
        # Check cache first
        self.cursor.execute('SELECT * FROM metadata_cache WHERE title = ?', (title,))
        cached = self.cursor.fetchone()
        if cached:
            return self._deserialize_metadata(cached)
        
        # Normalize and search
        normalized = self.normalize_title(title)
        params = {
            'api_key': self.api_key,
            'query': normalized
        }
        
        try:
            response = self.session.get(f"{self.base_url}/search/movie", params=params)
            response.raise_for_status()
            data = response.json()
            
            if data['results']:
                result = data['results'][0]  # Take first result
                metadata = self._extract_metadata(result)
                self._cache_metadata(title, metadata)
                return metadata
        except Exception as e:
            print(f"TMDB search error for {title}: {e}")
            
        return None
    
    def _extract_metadata(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract relevant metadata from TMDB result"""
        return {
            'tmdb_id': result.get('id'),
            'poster_url': f"https://image.tmdb.org/t/p/w500{result.get('poster_path', '')}" if result.get('poster_path') else None,
            'backdrop_url': f"https://image.tmdb.org/t/p/w780{result.get('backdrop_path', '')}" if result.get('backdrop_path') else None,
            'cast': self._get_cast(result.get('id')),
            'rating': result.get('vote_average'),
            'synopsis': result.get('overview'),
            'genres': [g['name'] for g in result.get('genres', [])],
            'year': int(result.get('release_date', '')[:4]) if result.get('release_date') else None
        }
    
    def _get_cast(self, tmdb_id: int) -> List[str]:
        """Get cast list for movie"""
        params = {'api_key': self.api_key}
        try:
            response = self.session.get(f"{self.base_url}/movie/{tmdb_id}/credits", params=params)
            response.raise_for_status()
            data = response.json()
            cast = [c['name'] for c in data.get('cast', [])[:5]]  # Top 5 actors
            return cast
        except:
            return []
    
    def _cache_metadata(self, title: str, metadata: Dict[str, Any]):
        """Cache metadata in SQLite"""
        self.cursor.execute('''
            INSERT OR REPLACE INTO metadata_cache 
            (title, tmdb_id, poster_url, backdrop_url, cast, rating, synopsis, genres, year)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            title,
            metadata.get('tmdb_id'),
            metadata.get('poster_url'),
            metadata.get('backdrop_url'),
            ','.join(metadata.get('cast', [])),
            metadata.get('rating'),
            metadata.get('synopsis'),
            ','.join(metadata.get('genres', [])),
            metadata.get('year')
        ))
        self.conn.commit()
    
    def _deserialize_metadata(self, cached: tuple) -> Dict[str, Any]:
        """Deserialize cached metadata"""
        return {
            'tmdb_id': cached[1],
            'poster_url': cached[2],
            'backdrop_url': cached[3],
            'cast': cached[4].split(',') if cached[4] else [],
            'rating': cached[5],
            'synopsis': cached[6],
            'genres': cached[7].split(',') if cached[7] else [],
            'year': cached[8]
        }
    
    def download_poster(self, url: str, filename: str) -> Optional[str]:
        """Download and compress poster image"""
        if not url:
            return None
            
        poster_dir = self.config['paths']['poster_dir']
        os.makedirs(poster_dir, exist_ok=True)
        
        output_path = os.path.join(poster_dir, f"{filename}.webp")
        
        # Check if already exists
        if os.path.exists(output_path):
            return output_path
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            # Open and compress image
            img = Image.open(io.BytesIO(response.content))
            
            # Resize if too large
            max_size = (800, 1200)
            img.thumbnail(max_size, Image.LANCZOS)
            
            # Convert to WebP with compression
            img.save(output_path, 'WebP', quality=85, optimize=True)
            
            # Check size limit
            size_kb = os.path.getsize(output_path) / 1024
            max_size_kb = self.config['poster']['max_size_kb']
            
            if size_kb > max_size_kb:
                os.remove(output_path)
                return None
                
            return output_path
            
        except Exception as e:
            print(f"Poster download error: {e}")
            return None
    
    def cleanup_old_posters(self, days: int = 30):
        """Remove posters older than specified days"""
        poster_dir = self.config['paths']['poster_dir']
        if not os.path.exists(poster_dir):
            return
            
        cutoff_time = time.time() - (days * 86400)
        
        for filename in os.listdir(poster_dir):
            filepath = os.path.join(poster_dir, filename)
            if os.path.getmtime(filepath) < cutoff_time:
                os.remove(filepath)
    
    def close(self):
        """Close database connection"""
        self.conn.close()
