"""
Multi-Format Export Module
Exports playlists to M3U, JSON, and XMLTV formats
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any
from playlist_parser import PlaylistEntry


class PlaylistExporter:
    """Export playlists to multiple formats"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.output_dir = config['paths']['output_dir']
        os.makedirs(self.output_dir, exist_ok=True)
    
    def export_m3u(self, entries: List[PlaylistEntry], filename: str = None) -> str:
        """Export to M3U format"""
        if not filename:
            filename = 'all.m3u'
        
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('#EXTM3U\n')
            for entry in entries:
                f.write(entry.to_m3u())
        
        return filepath
    
    def export_json(self, entries: List[PlaylistEntry], filename: str = None) -> str:
        """Export to JSON format with full metadata"""
        if not filename:
            filename = 'metadata.json'
        
        filepath = os.path.join(self.output_dir, filename)
        
        data = {
            'generated_at': datetime.now().isoformat(),
            'total_entries': len(entries),
            'entries': [e.to_dict() for e in entries]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    def export_xmltv(self, entries: List[PlaylistEntry], filename: str = None) -> str:
        """Export to XMLTV EPG format"""
        if not filename:
            filename = 'epg.xml'
        
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write('<tv>\n')
            
            for entry in entries:
                if entry.tvg_id:
                    f.write(f'  <channel id="{entry.tvg_id}">\n')
                    f.write(f'    <display-name>{entry.title}</display-name>\n')
                    f.write(f'    <icon src="{entry.tvg_logo}" />\n')
                    f.write('  </channel>\n')
            
            f.write('</tv>\n')
        
        return filepath
    
    def export_by_category(self, entries: List[PlaylistEntry]) -> Dict[str, str]:
        """Export separate playlists by category"""
        category_files = {}
        
        # Group by category
        categories = {}
        for entry in entries:
            category = entry.group_title or 'Uncategorized'
            if category not in categories:
                categories[category] = []
            categories[category].append(entry)
        
        # Export each category
        for category, cat_entries in categories.items():
            safe_name = category.lower().replace(' ', '-').replace('/', '-')
            filename = f'{safe_name}.m3u'
            filepath = self.export_m3u(cat_entries, filename)
            category_files[category] = filepath
        
        return category_files
    
    def export_combined(self, entries: List[PlaylistEntry], 
                       categories: List[str] = None) -> str:
        """Export combined playlist with category prefixes"""
        if categories:
            filtered = [e for e in entries if e.group_title in categories]
        else:
            filtered = entries
        
        filename = 'all.m3u'
        
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('#EXTM3U\n')
            
            for entry in filtered:
                # Add category prefix to title
                if entry.group_title:
                    entry.title = f"[{entry.group_title}] {entry.title}"
                f.write(entry.to_m3u())
        
        return filepath
