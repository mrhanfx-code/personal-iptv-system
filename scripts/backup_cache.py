"""
Backup script for cache directory
Backs up metadata.db and poster cache to external storage
"""

import os
import shutil
import sqlite3
from datetime import datetime
import json


def load_backup_config():
    """Load backup configuration"""
    config_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'backup_config.json')
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except:
        return {'enabled': False, 'external_storage': ''}


def backup_metadata_db(cache_dir, backup_dir):
    """Backup SQLite metadata database"""
    db_path = os.path.join(cache_dir, 'metadata.db')
    if not os.path.exists(db_path):
        return False
    
    os.makedirs(backup_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join(backup_dir, f'metadata_{timestamp}.db')
    
    # Use SQLite backup API
    conn = sqlite3.connect(db_path)
    backup_conn = sqlite3.connect(backup_path)
    conn.backup(backup_conn)
    backup_conn.close()
    conn.close()
    
    print(f"Backed up metadata.db to {backup_path}")
    return True


def backup_posters(cache_dir, backup_dir):
    """Backup poster images"""
    poster_dir = os.path.join(cache_dir, 'posters')
    if not os.path.exists(poster_dir):
        return False
    
    os.makedirs(backup_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join(backup_dir, f'posters_{timestamp}')
    
    shutil.copytree(poster_dir, backup_path)
    print(f"Backed up posters to {backup_path}")
    return True


def cleanup_old_backups(backup_dir, keep_count=5):
    """Remove old backups, keeping only the most recent"""
    if not os.path.exists(backup_dir):
        return
    
    # Get all backup files sorted by modification time
    files = []
    for item in os.listdir(backup_dir):
        item_path = os.path.join(backup_dir, item)
        if os.path.isfile(item_path):
            files.append((item_path, os.path.getmtime(item_path)))
    
    # Sort by time (newest first)
    files.sort(key=lambda x: x[1], reverse=True)
    
    # Remove old backups
    for item_path, _ in files[keep_count:]:
        os.remove(item_path)
        print(f"Removed old backup: {item_path}")


def main():
    """Main backup process"""
    config = load_backup_config()
    
    if not config.get('enabled'):
        print("Backup is disabled in configuration")
        return
    
    cache_dir = os.path.join(os.path.dirname(__file__), '..', 'cache')
    backup_dir = config.get('external_storage') or os.path.join(cache_dir, 'backups')
    
    print("Starting cache backup...")
    
    # Backup metadata database
    backup_metadata_db(cache_dir, backup_dir)
    
    # Backup posters
    backup_posters(cache_dir, backup_dir)
    
    # Cleanup old backups
    cleanup_old_backups(backup_dir, keep_count=5)
    
    print("Backup complete!")


if __name__ == '__main__':
    main()
