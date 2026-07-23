# Maintenance Guide

## Weekly Tasks

### Monday: Source Health Check
- Run `python scripts/source_monitor.py` to check source availability
- Review health report in `data/health_report.json`
- Deactivate sources with <50% uptime
- Update `data/sources.json` if needed

### Wednesday: Cache Cleanup
- Run `python scripts/cleanup_posters.py` to remove old posters
- Check cache directory size
- Verify SQLite database integrity
- Run `python scripts/backup_cache.py` if backup is enabled

### Friday: System Validation
- Run `python scripts/test_playlists.py` to validate playlists
- Check GitHub Actions workflow logs
- Verify GitHub Pages deployment
- Test web interface functionality

## Monthly Tasks

### First Week: TMDB API Review
- Check TMDB API usage in dashboard
- Verify rate limits are not being exceeded
- Review caching effectiveness
- Update confidence thresholds if needed

### Second Week: Source Review
- Review all source repositories for updates
- Add new sources if discovered
- Remove deprecated sources
- Update source priorities

### Third Week: Performance Review
- Monitor GitHub Actions execution time
- Check for timeout warnings
- Optimize chunk sizes if needed
- Review storage usage on GitHub Pages

### Fourth Week: Security Review
- Rotate API keys if recommended
- Review GitHub repository permissions
- Check for any security advisories
- Update dependencies

## Quarterly Tasks

### Backup Verification
- Test backup restoration procedure
- Verify external storage is accessible
- Check backup retention policy
- Update backup configuration if needed

### System Updates
- Update Python dependencies
- Review GitHub Actions for deprecated actions
- Test system with latest Python version
- Update documentation

### Feature Review
- Review user feedback (if applicable)
- Plan new features or improvements
- Update implementation plan
- Refactor code if needed

## Emergency Procedures

### Source Failure
1. Run `python scripts/source_monitor.py`
2. Identify failed sources
3. Deactivate in `data/sources.json`
4. Commit and push changes
5. GitHub Actions will use remaining sources

### TMDB API Outage
1. System will fall back to raw titles
2. Monitor TMDB status page
3. Check API key status
4. Temporary disable enrichment if needed

### GitHub Actions Failure
1. Check workflow logs for error details
2. Verify GitHub Secrets are set correctly
3. Test workflow locally using `act`
4. Re-run workflow after fixing issues

### Storage Limit Reached
1. Run `python scripts/cleanup_posters.py`
2. Reduce poster retention period in config
3. Manually delete old output files
4. Consider reducing number of sources

## Monitoring

### Key Metrics to Track
- Total stream count
- Stream availability percentage
- TMDB enrichment success rate
- GitHub Actions execution time
- GitHub Pages storage usage
- Source uptime percentages

### Alerts to Watch For
- Workflow execution time > 5 hours
- Stream availability < 80%
- TMDB API rate limit warnings
- Storage usage > 80% of limit
- Source uptime < 50%
