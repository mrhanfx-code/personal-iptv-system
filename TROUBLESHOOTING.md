# Troubleshooting Guide

## Common Issues and Solutions

### TMDB API Issues

**Problem**: TMDB API returns 401 Unauthorized
- **Solution**: Verify your API key is correct in `data/config.json` and GitHub Secrets
- **Solution**: Check if your API key has been revoked or expired

**Problem**: TMDB rate limit exceeded
- **Solution**: The system implements caching and request queuing. Wait 24 hours for rate limit reset
- **Solution**: Reduce the number of sources in `data/sources.json`

**Problem**: No metadata being enriched
- **Solution**: Check if TMDB API key is set correctly
- **Solution**: Verify network connectivity to api.themoviedb.org
- **Solution**: Check cache/metadata.db for existing cached entries

### GitHub Actions Issues

**Problem**: Workflow fails with timeout
- **Solution**: The workflow has a 6-hour timeout. Check if processing is taking too long
- **Solution**: Reduce chunk size in enrichment step
- **Solution**: Disable stream validation to speed up processing

**Problem**: GitHub Pages deployment fails
- **Solution**: Ensure repository has GitHub Pages enabled in settings
- **Solution**: Check that gh-pages branch exists
- **Solution**: Verify GITHUB_TOKEN has correct permissions

**Problem**: Workflow fails on dependency installation
- **Solution**: Check Python version is 3.11+
- **Solution**: Verify all dependencies are listed in workflow file

### Playlist Parsing Issues

**Problem**: Source URLs return 404
- **Solution**: Source repositories may have moved. Update URLs in `data/sources.json`
- **Solution**: Check if source repository is still active

**Problem**: Duplicate entries in output
- **Solution**: The system implements duplicate detection. Check if sources have overlapping content
- **Solution**: Review `scripts/playlist_parser.py` duplicate detection logic

**Problem**: Invalid M3U format
- **Solution**: Verify source URLs return valid M3U content
- **Solution**: Check for malformed EXTINF tags in source playlists

### Web Interface Issues

**Problem**: Web interface not loading
- **Solution**: Ensure GitHub Pages is deployed correctly
- **Solution**: Check browser console for JavaScript errors
- **Solution**: Verify output/metadata.json exists and is valid JSON

**Problem**: NSFW section not accessible
- **Solution**: Age verification must be completed. Check localStorage
- **Solution**: Ensure NSFW content exists in playlists

### Storage Issues

**Problem**: GitHub Pages storage limit exceeded
- **Solution**: The system implements poster compression (200KB max) and 30-day cleanup
- **Solution**: Manually run `python scripts/cleanup_posters.py`
- **Solution**: Reduce number of poster images cached

**Problem**: SQLite database locked
- **Solution**: Close any running processes accessing cache/metadata.db
- **Solution**: Check for multiple instances of the script running

### Performance Issues

**Problem**: Processing takes too long
- **Solution**: Reduce number of sources in `data/sources.json`
- **Solution**: Increase chunk size in enrichment step
- **Solution**: Disable stream validation for faster processing

**Problem**: High memory usage
- **Solution**: Process playlists in smaller batches
- **Solution**: Clear cache directory periodically

## Getting Help

If you encounter issues not covered here:
1. Check the [GitHub Issues](https://github.com/mrhanfx-code/personal-iptv-system/issues)
2. Review the [main README](README.md)
3. Check logs in GitHub Actions for detailed error messages
