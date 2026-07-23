"""
Metadata Enrichment Pipeline
Merges TMDB metadata with playlist entries and manages batch processing
"""

import json
import os
from typing import List, Dict, Any
from tmdb_client import TMDBClient
from playlist_parser import PlaylistEntry


class MetadataEnricher:
    """Enrich playlist entries with TMDB metadata"""
    
    def __init__(self, tmdb_client: TMDBClient, config: Dict[str, Any]):
        self.tmdb = tmdb_client
        self.config = config
        self.stats = {
            'total': 0,
            'enriched': 0,
            'failed': 0,
            'cached': 0
        }
    
    def enrich_entry(self, entry: PlaylistEntry) -> PlaylistEntry:
        """Enrich single entry with TMDB metadata"""
        self.stats['total'] += 1
        
        # Skip if already has metadata
        if entry.tvg_logo and entry.tvg_logo.startswith('http'):
            return entry
        
        # Search TMDB
        metadata = self.tmdb.search_movie(entry.title)
        
        if metadata:
            self.stats['enriched'] += 1
            
            # Add poster URL
            if metadata.get('poster_url'):
                # Download and cache poster
                safe_filename = entry.title.replace('/', '_').replace(' ', '_')
                poster_path = self.tmdb.download_poster(
                    metadata['poster_url'], 
                    safe_filename
                )
                
                if poster_path:
                    # Use local path for tvg-logo
                    entry.tvg_logo = f"cache/posters/{safe_filename}.webp"
                else:
                    entry.tvg_logo = metadata['poster_url']
            
            # Add custom attributes (stored in tvg-name or as custom fields)
            if metadata.get('cast'):
                entry.tvg_name = f"{entry.title} | Cast: {', '.join(metadata['cast'][:3])}"
            
            if metadata.get('rating'):
                entry.tvg_name = f"{entry.tvg_name} | Rating: {metadata['rating']}/10"
            
            if metadata.get('genres'):
                entry.tvg_name = f"{entry.tvg_name} | Genre: {', '.join(metadata['genres'][:2])}"
            
            if metadata.get('year'):
                entry.tvg_name = f"{entry.tvg_name} | Year: {metadata['year']}"
            
        else:
            self.stats['failed'] += 1
        
        return entry
    
    def enrich_batch(self, entries: List[PlaylistEntry], 
                    chunk_size: int = 50) -> List[PlaylistEntry]:
        """Enrich entries in batches to manage API rate limits"""
        enriched = []
        
        for i in range(0, len(entries), chunk_size):
            chunk = entries[i:i + chunk_size]
            
            for entry in chunk:
                enriched_entry = self.enrich_entry(entry)
                enriched.append(enriched_entry)
            
            # Progress logging
            print(f"Processed {min(i + chunk_size, len(entries))}/{len(entries)} entries")
        
        return enriched
    
    def validate_metadata(self, entry: PlaylistEntry) -> bool:
        """Validate enriched metadata"""
        if not entry.title:
            return False
        
        if not entry.url:
            return False
        
        return True
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get enrichment statistics"""
        total = self.stats['total']
        enriched = self.stats['enriched']
        
        return {
            **self.stats,
            'success_rate': (enriched / total * 100) if total > 0 else 0
        }
