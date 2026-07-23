# User Guide

## Getting Started

### Prerequisites

- GitHub account (free tier)
- TMDB API key (free tier)
- Python 3.11+ (for local development)
- Git

### Step 1: Obtain TMDB API Key

1. Visit [themoviedb.org](https://www.themoviedb.org/)
2. Sign up for a free account
3. Navigate to Settings → API
4. Click "Request an API Key"
5. Select "Developer" as the key type
6. Fill in the application details:
   - Application name: Personal IPTV System
   - Application URL: https://github.com/mrhanfx-code/personal-iptv-system
   - Application summary: Personal IPTV playlist management system
7. Submit and wait for approval (usually instant)
8. Copy your API key (starts with a hash like `#1234567890abcdef`)

### Step 2: Clone and Configure

```bash
git clone https://github.com/mrhanfx-code/personal-iptv-system.git
cd personal-iptv-system
```

Edit `data/config.json` and replace `YOUR_TMDB_API_KEY_HERE` with your actual API key.

### Step 3: Install Dependencies

```bash
pip install requests m3u8 tmdbv3api fuzzywuzzy Pillow
```

### Step 4: Run Locally

```bash
python scripts/main.py
```

This will:
- Download source playlists
- Parse and validate streams
- Enrich with TMDB metadata
- Export to M3U, JSON, and XMLTV formats
- Save outputs to the `output/` directory

## Using the System

### Local Usage

**Generate Playlists:**
```bash
python scripts/main.py
```

**Test Playlists:**
```bash
python scripts/test_playlists.py
```

**Monitor Source Health:**
```bash
python scripts/source_monitor.py
```

**Backup Cache:**
```bash
python scripts/backup_cache.py
```

### GitHub Actions Automation

The system runs automatically daily at midnight UTC. To trigger manually:

1. Go to repository Actions tab
2. Select "Daily IPTV Playlist Update"
3. Click "Run workflow"
4. Choose branch (usually `master`)
5. Click "Run workflow" button

### Web Interface

Access the web interface at your GitHub Pages URL:
`https://mrhanfx-code.github.io/personal-iptv-system/`

**Features:**
- **Status Dashboard**: View last update time, stream counts, and category breakdowns
- **Search**: Filter by title or genre
- **Category Filters**: Toggle between Live TV, VOD, and NSFW
- **NSFW Section**: Age verification required (18+)
- **Download Buttons**: Get M3U, JSON, or XMLTV formats

### Using Playlists in Players

**VLC Media Player:**
1. Download `output/all.m3u`
2. Open VLC → Media → Open Network Stream
3. Browse to the downloaded M3U file
4. Click Play

**Kodi:**
1. Install PVR IPTV Simple Client add-on
2. Configure with M3U URL: `https://mrhanfx-code.github.io/personal-iptv-system/output/all.m3u`
3. Enable EPG with XMLTV URL: `https://mrhanfx-code.github.io/personal-iptv-system/output/epg.xml`

**IPTV Smarters Pro:**
1. Add playlist with M3U URL
2. Use `https://mrhanfx-code.github.io/personal-iptv-system/output/all.m3u`
3. Enable EPG with XMLTV URL

## Configuration

### Editing Sources

Edit `data/sources.json` to add or remove playlist sources:

```json
{
  "live_tv": [
    {
      "name": "Source Name",
      "url": "https://example.com/playlist.m3u",
      "category": "Live TV"
    }
  ]
}
```

### Adjusting TMDB Settings

Edit `data/config.json`:

```json
{
  "tmdb": {
    "confidence_threshold": 0.75,
    "rate_limit": 1000
  }
}
```

- `confidence_threshold`: Lower = more matches, higher = more accurate (0.7-0.8 recommended)
- `rate_limit`: Maximum TMDB API requests per day (free tier: 1000)

### Quality Filtering

Edit `data/config.json`:

```json
{
  "quality": {
    "min_resolution": "720p",
    "preferred_qualities": ["4K", "1080p", "720p"]
  }
}
```

## Troubleshooting

### TMDB API Errors

**401 Unauthorized**: Check your API key in `data/config.json` and GitHub Secrets
**429 Too Many Requests**: Wait 24 hours for rate limit reset, or reduce number of sources

### GitHub Actions Failures

**Timeout**: Reduce chunk size or disable stream validation
**Deployment Failed**: Ensure GitHub Pages is enabled in repository settings

### Stream Availability

**Dead Links**: Run `python scripts/source_monitor.py` to identify failed sources
**Geo-blocking**: Some streams may be region-locked; consider using VPN

## Advanced Usage

### Custom Categories

Add custom categories in `data/sources.json` and filter accordingly in the web interface.

### Backup Configuration

Edit `data/backup_config.json` to configure external storage for cache backups.

### Custom Domain

1. Purchase domain from registrar
2. Add CNAME record pointing to `mrhanfx-code.github.io`
3. Create `CNAME` file in repository root with your domain
4. Enable custom domain in GitHub Pages settings

## Security Notes

- Never commit your TMDB API key to the repository
- Always use GitHub Secrets for sensitive data
- Keep repository private for personal use
- NSFW content is separated and requires age verification
