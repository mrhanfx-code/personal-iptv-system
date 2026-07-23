"""
Playlist Validation and Testing Script
Tests stream availability, TMDB matching, and format compliance
"""

import requests
from tmdb_client import TMDBClient
from playlist_parser import PlaylistParser
import json
import os


def test_stream_availability(entries, sample_size=0.1):
    """Test stream availability (sample percentage)"""
    sample_count = max(1, int(len(entries) * sample_size))
    sample_entries = entries[:sample_count]
    
    available = 0
    for entry in sample_entries:
        try:
            response = requests.head(entry.url, timeout=5)
            if response.status_code < 400:
                available += 1
        except:
            pass
    
    success_rate = (available / sample_count * 100) if sample_count > 0 else 0
    print(f"Stream availability: {available}/{sample_count} ({success_rate:.1f}%)")
    return success_rate


def test_tmdb_matching(titles, api_key):
    """Test TMDB matching accuracy"""
    config = {
        'tmdb': {'api_key': api_key},
        'paths': {'cache_dir': 'cache', 'poster_dir': 'cache/posters'}
    }
    
    tmdb = TMDBClient(api_key, config)
    
    matched = 0
    for title in titles:
        result = tmdb.search_movie(title)
        if result:
            matched += 1
    
    success_rate = (matched / len(titles) * 100) if titles else 0
    print(f"TMDB matching: {matched}/{len(titles)} ({success_rate:.1f}%)")
    
    tmdb.close()
    return success_rate


def test_m3u_compliance(entries):
    """Test M3U output format compliance"""
    errors = []
    
    for entry in entries:
        if not entry.url:
            errors.append(f"Missing URL: {entry.title}")
        if not entry.title:
            errors.append(f"Missing title: {entry.url}")
        if entry.duration and not isinstance(entry.duration, int):
            errors.append(f"Invalid duration: {entry.title}")
    
    print(f"M3U compliance: {len(errors)} errors found")
    return len(errors) == 0


def run_all_tests():
    """Run all validation tests"""
    print("Running playlist validation tests...\n")
    
    # Load configuration
    config_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'config.json')
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Load sources
    sources_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'sources.json')
    with open(sources_path, 'r') as f:
        sources = json.load(f)
    
    # Parse playlists
    parser = PlaylistParser(config)
    all_sources = sources['live_tv'] + sources['vod']
    entries = parser.merge_playlists(all_sources)
    
    print(f"Total entries to test: {len(entries)}\n")
    
    # Run tests
    test_stream_availability(entries, sample_size=0.1)
    
    # Test TMDB with sample titles
    sample_titles = [e.title for e in entries[:10]]
    test_tmdb_matching(sample_titles, config['tmdb']['api_key'])
    
    test_m3u_compliance(entries)
    
    print("\nAll tests complete!")


if __name__ == '__main__':
    run_all_tests()
