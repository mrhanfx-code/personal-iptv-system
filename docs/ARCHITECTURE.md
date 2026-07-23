# Architecture Documentation

## System Overview

The Personal IPTV System is a modular Python application that aggregates IPTV playlists from multiple sources, enriches them with TMDB metadata, and exports to multiple formats with daily automation via GitHub Actions.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     GitHub Actions                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Schedule   │→ │   Download   │→ │   Enrich     │      │
│  │   Trigger    │  │   Playlists  │  │   Metadata   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                    ↓         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Export     │→ │   Commit     │→ │   Deploy     │      │
│  │   Formats    │  │   & Push     │  │   Pages      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                     Local Processing                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Playlist   │→ │   TMDB       │→ │   Exporter   │      │
│  │   Parser     │  │   Client     │  │             │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         ↓                  ↓                  ↓              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   SQLite     │  │   Poster     │  │   Output     │      │
│  │   Cache      │  │   Cache      │  │   Files      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                     Web Interface                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Status     │  │   Search     │  │   Download   │      │
│  │   Dashboard  │  │   & Filter   │  │   Buttons    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## Component Architecture

### 1. Playlist Parser (`scripts/playlist_parser.py`)

**Responsibilities:**
- Parse M3U/M3U8 playlist files
- Extract EXTINF tags and metadata
- Validate stream URLs
- Detect duplicates
- Identify stream quality
- Merge multiple playlists

**Key Classes:**
- `PlaylistEntry`: Represents a single playlist item
- `PlaylistParser`: Orchestrates parsing and validation

**Data Flow:**
```
Source URL → Download → Parse → Validate → Enrich → Export
```

### 2. TMDB Client (`scripts/tmdb_client.py`)

**Responsibilities:**
- TMDB API integration
- Title normalization
- Fuzzy string matching
- Metadata retrieval
- Poster download and caching
- SQLite cache management

**Key Classes:**
- `TMDBClient`: Main API wrapper with caching

**Caching Strategy:**
- SQLite database for metadata (cache/metadata.db)
- File system for poster images (cache/posters/)
- TTL: 30 days for posters, indefinite for metadata

**Rate Limiting:**
- Request queue with priority (VOD > Live TV)
- Batch API calls where possible
- Configurable confidence threshold

### 3. Metadata Enricher (`scripts/enricher.py`)

**Responsibilities:**
- Merge TMDB data with playlist entries
- Batch processing for large playlists
- Progress tracking
- Statistics reporting

**Key Classes:**
- `MetadataEnricher`: Orchestrates enrichment pipeline

**Batch Processing:**
- Chunk size: 50 entries per batch
- Progress logging every chunk
- Configurable chunk size for optimization

### 4. Exporter (`scripts/exporter.py`)

**Responsibilities:**
- Export to M3U format
- Export to JSON format
- Export to XMLTV EPG format
- Category-based exports
- Combined exports

**Key Classes:**
- `PlaylistExporter`: Handles all export operations

**Output Formats:**
- M3U: Standard playlist format with enriched EXTINF tags
- JSON: Full metadata structure for web interface
- XMLTV: Electronic program guide data

### 5. GitHub Actions Workflow (`.github/workflows/daily-update.yml`)

**Workflow Steps:**
1. Checkout repository
2. Setup Python 3.11
3. Install dependencies
4. Download source playlists
5. Enrich with TMDB metadata
6. Export to multiple formats
7. Commit and push changes
8. Deploy to GitHub Pages
9. Cleanup old posters

**Triggers:**
- Schedule: Daily at midnight UTC
- Manual: workflow_dispatch

**Timeout Handling:**
- 6-hour limit with 5-hour warning
- Chunked processing to avoid timeout
- Retry logic with exponential backoff

## Data Flow

### Input Sources
```
data/sources.json → Multiple M3U URLs → Playlist Parser
```

### Processing Pipeline
```
Raw Playlists → Parse → Validate → Enrich → Export → Output Files
```

### Caching Layer
```
TMDB API → SQLite Cache → Metadata Enricher
Poster URLs → File Cache → Playlist Export
```

### Output
```
output/
├── all.m3u (combined playlist)
├── live-tv.m3u (Live TV only)
├── vod.m3u (VOD only)
├── nsfw.m3u (NSFW only)
├── epg.xml (XMLTV EPG)
└── metadata.json (full metadata)
```

## Database Schema

### metadata.db (SQLite)

**Table: metadata_cache**
```sql
CREATE TABLE metadata_cache (
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
```

**Indexes:**
- Primary key on title
- Index on tmdb_id for lookups

## Configuration Management

### config.json Structure
```json
{
  "tmdb": {
    "api_key": "string",
    "confidence_threshold": 0.75,
    "rate_limit": 1000,
    "cache_enabled": true
  },
  "paths": {
    "cache_dir": "cache",
    "poster_dir": "cache/posters",
    "metadata_db": "cache/metadata.db",
    "output_dir": "output"
  },
  "poster": {
    "max_size_kb": 200,
    "format": "WebP",
    "retention_days": 30
  },
  "quality": {
    "min_resolution": "720p",
    "preferred_qualities": ["4K", "1080p", "720p"]
  }
}
```

## Security Considerations

### API Key Management
- Never commit API keys to repository
- Use GitHub Secrets for TMDB_API_KEY
- Environment variable injection in GitHub Actions

### NSFW Content
- Separate playlist output
- Age verification in web interface
- Client-side localStorage for preferences
- Explicit warnings and disclaimers

### Data Privacy
- Private repository for personal use
- No user data collection
- Local cache only (no external storage unless configured)

## Performance Optimization

### Caching Strategy
- SQLite metadata cache reduces TMDB API calls
- Poster image caching avoids re-downloads
- Configurable cache TTL

### Batch Processing
- Chunk-based processing (50 entries per chunk)
- Progress logging for monitoring
- Configurable chunk size

### Rate Limiting
- Request queue with priority
- Batch API calls where possible
- Exponential backoff on failures

## Scalability Considerations

### Current Limitations
- TMDB API: 1,000 requests/day
- GitHub Actions: 2,000 minutes/month
- GitHub Pages: 1GB soft storage, 100GB hard

### Scaling Strategies
- Reduce source count to stay within limits
- Increase chunk size for faster processing
- Implement external storage for backups
- Consider self-hosting for larger scale

## Monitoring and Observability

### Health Checks
- Source availability monitoring
- Stream validation sampling
- TMDB API usage tracking
- GitHub Actions execution time

### Logging
- Progress logging during enrichment
- Error logging for failed operations
- Statistics reporting after each run

### Metrics
- Total stream count
- Enrichment success rate
- Stream availability percentage
- Source uptime percentages
