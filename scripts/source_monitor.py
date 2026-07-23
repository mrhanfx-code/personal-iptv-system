"""
Source Health Monitoring Script
Checks source URL availability and implements automatic rotation on failure
"""

import requests
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List


def load_sources():
    """Load source URLs from data/sources.json"""
    sources_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'sources.json')
    with open(sources_path, 'r') as f:
        return json.load(f)


def check_source_health(url: str) -> Dict[str, any]:
    """Check if source URL is accessible"""
    try:
        response = requests.head(url, timeout=10)
        return {
            'url': url,
            'status': response.status_code,
            'accessible': response.status_code < 400,
            'checked_at': datetime.now().isoformat()
        }
    except Exception as e:
        return {
            'url': url,
            'status': 'error',
            'accessible': False,
            'error': str(e),
            'checked_at': datetime.now().isoformat()
        }


def get_uptime_stats(health_data: List[Dict]) -> Dict[str, float]:
    """Calculate uptime statistics from health check history"""
    if not health_data:
        return {'uptime': 0, 'total_checks': 0}
    
    accessible_count = sum(1 for check in health_data if check.get('accessible'))
    total_checks = len(health_data)
    uptime = (accessible_count / total_checks * 100) if total_checks > 0 else 0
    
    return {
        'uptime': uptime,
        'total_checks': total_checks,
        'last_check': health_data[-1].get('checked_at')
    }


def rotate_failed_sources(sources: Dict, health_data: Dict):
    """Rotate out sources with poor uptime"""
    for category, source_list in sources.items():
        if category == 'epg':
            continue  # Skip EPG rotation
        
        for i, source in enumerate(source_list):
            url = source['url']
            stats = health_data.get(url, {})
            uptime = stats.get('uptime', 100)
            
            # If uptime below 50%, mark as inactive
            if uptime < 50:
                source['active'] = False
                print(f"Deactivated {source['name']} (uptime: {uptime:.1f}%)")
            else:
                source['active'] = True
    
    return sources


def save_health_report(health_data: Dict):
    """Save health check report"""
    report_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'health_report.json')
    with open(report_path, 'w') as f:
        json.dump(health_data, f, indent=2)


def main():
    """Main monitoring process"""
    print("Running source health check...")
    
    sources = load_sources()
    health_data = {}
    
    # Check all sources
    all_sources = sources['live_tv'] + sources['vod'] + sources['nsfw']
    
    for source in all_sources:
        print(f"Checking {source['name']}...")
        health = check_source_health(source['url'])
        health_data[source['url']] = [health]
    
    # Save health report
    save_health_report(health_data)
    
    print(f"Health check complete: {len(all_sources)} sources checked")


if __name__ == '__main__':
    main()
