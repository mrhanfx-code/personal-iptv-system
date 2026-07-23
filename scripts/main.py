"""
Main entry point for IPTV playlist processing
Orchestrates download, enrichment, and export
"""

import json
import os
from tmdb_client import TMDBClient
from playlist_parser import PlaylistParser
from enricher import MetadataEnricher
from exporter import PlaylistExporter


def load_config():
    """Load configuration from data/config.json"""
    config_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'config.json')
    with open(config_path, 'r') as f:
        return json.load(f)


def load_sources():
    """Load source URLs from data/sources.json"""
    sources_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'sources.json')
    with open(sources_path, 'r') as f:
        return json.load(f)


def main():
    """Main processing pipeline"""
    print("Starting IPTV playlist processing...")
    
    # Load configuration
    config = load_config()
    sources = load_sources()
    
    # Initialize components
    parser = PlaylistParser(config)
    tmdb_client = TMDBClient(config['tmdb']['api_key'], config)
    enricher = MetadataEnricher(tmdb_client, config)
    exporter = PlaylistExporter(config)
    
    # Download and parse playlists
    print("Downloading source playlists...")
    all_sources = sources['live_tv'] + sources['vod'] + sources['nsfw']
    entries = parser.merge_playlists(all_sources)
    
    print(f"Parsed {len(entries)} entries")
    
    # Validate streams (disabled for performance - can be enabled for testing)
    print("Skipping stream validation for performance...")
    # for entry in entries:
    #     parser.validate_stream(entry)
    #     parser.detect_quality(entry)
    
    # Enrich with TMDB metadata
    print("Enriching with TMDB metadata...")
    enriched_entries = enricher.enrich_batch(entries, chunk_size=50)
    
    # Print statistics
    stats = enricher.get_statistics()
    print(f"Enrichment stats: {stats}")
    
    # Export to multiple formats
    print("Exporting to multiple formats...")
    exporter.export_m3u(enriched_entries)
    exporter.export_json(enriched_entries)
    exporter.export_xmltv(enriched_entries)
    exporter.export_by_category(enriched_entries)
    exporter.export_combined(enriched_entries)
    
    # Cleanup old posters
    print("Cleaning up old posters...")
    tmdb_client.cleanup_old_posters(days=30)
    
    # Close connections
    tmdb_client.close()
    
    print("Processing complete!")


if __name__ == '__main__':
    main()
