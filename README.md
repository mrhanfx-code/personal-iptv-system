# Personal IPTV System

Comprehensive personal IPTV playlist system with automatic TMDB metadata enrichment, poster images, daily updates, and multi-format export.

## Features

- **Live TV, VOD, and NSFW Content**: Aggregates from free GitHub sources
- **TMDB Metadata Integration**: Automatic poster images, cast, ratings, synopses
- **Daily Automation**: GitHub Actions workflow for automatic updates
- **Multi-Format Export**: M3U, JSON, XMLTV EPG formats
- **Web Interface**: Playlist management with search, filter, and preview
- **Zero Cost**: Uses free GitHub services and TMDB API

## Setup

### Prerequisites

- GitHub account (free tier)
- TMDB API key (free tier, 1,000 requests/day)
- Python 3.11+ (for local development)
- Git

### TMDB API Key Setup

1. Sign up at [themoviedb.org](https://www.themoviedb.org/)
2. Apply for an API key
3. Retrieve API key from account settings
4. Add as GitHub Secret: `TMDB_API_KEY`

### Installation

1. Clone repository
2. Install dependencies: `pip install requests m3u8 tmdbv3api fuzzywuzzy Pillow`
3. Configure `data/config.json` with your settings
4. Run locally: `python scripts/main.py`

### GitHub Actions

The workflow runs daily at midnight UTC. Manual triggers available via Actions tab.

## Project Structure

```
.github/workflows/  # GitHub Actions automation
data/                # Configuration and source URLs
output/              # Generated playlists
scripts/             # Python modules
cache/               # Metadata and poster cache
web/                 # Web interface
```

## Usage

### Local Development

```bash
# Download and process playlists
python scripts/main.py

# Test playlists
python scripts/test_playlists.py
```

### Web Interface

Access via GitHub Pages or run locally:
```bash
python -m http.server 8000 --directory web
```

## License

Personal use only. Private repository.
