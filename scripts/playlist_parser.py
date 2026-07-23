"""
M3U Playlist Parser and Merger
Handles parsing, validation, merging, and quality detection for IPTV playlists
"""

import requests
import re
from typing import List, Dict, Any, Optional, Set
from urllib.parse import urlparse
import m3u8


class PlaylistEntry:
    """Represents a single entry in an M3U playlist"""
    
    def __init__(self, url: str, title: str, duration: int = -1, 
                 tvg_id: str = None, tvg_name: str = None, 
                 tvg_logo: str = None, group_title: str = None):
        self.url = url
        self.title = title
        self.duration = duration
        self.tvg_id = tvg_id
        self.tvg_name = tvg_name
        self.tvg_logo = tvg_logo
        self.group_title = group_title
        self.quality = None
        self.valid = True
        self.geo_blocked = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON export"""
        return {
            'url': self.url,
            'title': self.title,
            'duration': self.duration,
            'tvg_id': self.tvg_id,
            'tvg_name': self.tvg_name,
            'tvg_logo': self.tvg_logo,
            'group_title': self.group_title,
            'quality': self.quality,
            'valid': self.valid,
            'geo_blocked': self.geo_blocked
        }
    
    def to_m3u(self) -> str:
        """Convert to M3U format line"""
        attrs = []
        if self.tvg_id:
            attrs.append(f'tvg-id="{self.tvg_id}"')
        if self.tvg_name:
            attrs.append(f'tvg-name="{self.tvg_name}"')
        if self.tvg_logo:
            attrs.append(f'tvg-logo="{self.tvg_logo}"')
        if self.group_title:
            attrs.append(f'group-title="{self.group_title}"')
        
        attr_str = ' '.join(attrs) if attrs else ''
        return f'#EXTINF:{self.duration} {attr_str},{self.title}\n{self.url}\n'


class PlaylistParser:
    """Parse and validate M3U playlists"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.entries: List[PlaylistEntry] = []
        self.seen_urls: Set[str] = set()
        self.seen_titles: Set[str] = set()
    
    def parse_url(self, url: str) -> List[PlaylistEntry]:
        """Parse M3U playlist from URL"""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return self.parse_content(response.text)
        except Exception as e:
            print(f"Error parsing {url}: {e}")
            return []
    
    def parse_file(self, filepath: str) -> List[PlaylistEntry]:
        """Parse M3U playlist from file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            return self.parse_content(content)
        except Exception as e:
            print(f"Error parsing {filepath}: {e}")
            return []
    
    def parse_content(self, content: str) -> List[PlaylistEntry]:
        """Parse M3U content string"""
        entries = []
        lines = content.split('\n')
        
        current_entry = None
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('#EXTINF:'):
                # Parse EXTINF line
                current_entry = self._parse_extinf(line)
            elif line and not line.startswith('#') and current_entry:
                # URL line
                current_entry.url = line
                entries.append(current_entry)
                current_entry = None
        
        return entries
    
    def _parse_extinf(self, line: str) -> PlaylistEntry:
        """Parse EXTINF tag"""
        # Format: #EXTINF:<duration> <attributes>,<title>
        match = re.match(r'#EXTINF:(-?\d+)\s+(.*)', line)
        if not match:
            return PlaylistEntry('', '', -1)
        
        duration = int(match.group(1))
        rest = match.group(2)
        
        # Split attributes and title
        if ',' in rest:
            attrs_part, title = rest.rsplit(',', 1)
        else:
            attrs_part = rest
            title = ''
        
        # Parse attributes
        tvg_id = self._extract_attr(attrs_part, 'tvg-id')
        tvg_name = self._extract_attr(attrs_part, 'tvg-name')
        tvg_logo = self._extract_attr(attrs_part, 'tvg-logo')
        group_title = self._extract_attr(attrs_part, 'group-title')
        
        return PlaylistEntry('', title.strip(), duration, tvg_id, tvg_name, tvg_logo, group_title)
    
    def _extract_attr(self, attrs_str: str, attr_name: str) -> Optional[str]:
        """Extract attribute value from EXTINF line"""
        pattern = rf'{attr_name}="([^"]*)"'
        match = re.search(pattern, attrs_str)
        return match.group(1) if match else None
    
    def validate_stream(self, entry: PlaylistEntry) -> bool:
        """Validate stream URL accessibility"""
        try:
            response = requests.head(entry.url, timeout=10, allow_redirects=True)
            
            # Check for geo-blocking (403)
            if response.status_code == 403:
                entry.geo_blocked = True
                return False
            
            # Check for other errors
            if response.status_code >= 400:
                entry.valid = False
                return False
            
            return True
        except Exception:
            entry.valid = False
            return False
    
    def detect_quality(self, entry: PlaylistEntry):
        """Detect stream quality from metadata"""
        # Try to infer quality from title
        title_lower = entry.title.lower()
        
        if '4k' in title_lower or 'uhd' in title_lower:
            entry.quality = '4K'
        elif '1080' in title_lower or 'fullhd' in title_lower or 'fhd' in title_lower:
            entry.quality = '1080p'
        elif '720' in title_lower or 'hd' in title_lower:
            entry.quality = '720p'
        else:
            entry.quality = 'SD'
    
    def add_entry(self, entry: PlaylistEntry, priority: int = 0):
        """Add entry with duplicate detection"""
        # URL-based duplicate check
        if entry.url in self.seen_urls:
            return False
        
        # Title-based duplicate check (optional)
        if entry.title in self.seen_titles:
            return False
        
        self.entries.append(entry)
        self.seen_urls.add(entry.url)
        self.seen_titles.add(entry.title)
        return True
    
    def merge_playlists(self, sources: List[Dict[str, str]], 
                      priority_map: Dict[str, int] = None) -> List[PlaylistEntry]:
        """Merge multiple playlists with priority-based conflict resolution"""
        if priority_map is None:
            priority_map = {}
        
        all_entries = []
        
        for source in sources:
            url = source['url']
            category = source['category']
            priority = priority_map.get(category, 0)
            
            entries = self.parse_url(url)
            
            for entry in entries:
                entry.group_title = category
                if self.add_entry(entry, priority):
                    all_entries.append(entry)
        
        return all_entries
    
    def filter_by_quality(self, min_quality: str = '720p') -> List[PlaylistEntry]:
        """Filter entries by minimum quality"""
        quality_order = {'4K': 4, '1080p': 3, '720p': 2, 'SD': 1}
        min_level = quality_order.get(min_quality, 1)
        
        return [e for e in self.entries 
                if quality_order.get(e.quality, 0) >= min_level]
    
    def filter_by_category(self, categories: List[str]) -> List[PlaylistEntry]:
        """Filter entries by category"""
        return [e for e in self.entries if e.group_title in categories]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get playlist statistics"""
        valid_count = sum(1 for e in self.entries if e.valid)
        invalid_count = len(self.entries) - valid_count
        geo_blocked_count = sum(1 for e in self.entries if e.geo_blocked)
        
        quality_counts = {}
        for entry in self.entries:
            q = entry.quality or 'Unknown'
            quality_counts[q] = quality_counts.get(q, 0) + 1
        
        return {
            'total': len(self.entries),
            'valid': valid_count,
            'invalid': invalid_count,
            'geo_blocked': geo_blocked_count,
            'quality_distribution': quality_counts
        }
