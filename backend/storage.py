"""Storage simulator for educational purposes."""

import os
import json


class StorageSimulator:
    """Simulates a phone file system for educational demonstrations."""

    def __init__(self, base_path=None):
        """Initialize storage simulator with optional base path."""
        self.base_path = base_path or os.path.join(os.path.dirname(__file__), '..', 'uploads')
        os.makedirs(self.base_path, exist_ok=True)

    def get_directory_structure(self, path=None, session_token=None):
        """Get directory structure for a session (simulating phone storage)."""
        if session_token:
            session_path = os.path.join(self.base_path, session_token)
        else:
            session_path = self.base_path

        if not os.path.isdir(session_path):
            return {'name': 'Storage', 'type': 'folder', 'contents': []}

        contents = []
        try:
            for name in sorted(os.listdir(session_path)):
                full_path = os.path.join(session_path, name)
                if os.path.isfile(full_path):
                    size = os.path.getsize(full_path)
                    contents.append({
                        'name': name,
                        'type': 'file',
                        'size': size,
                        'path': name
                    })
                elif os.path.isdir(full_path):
                    contents.append({
                        'name': name,
                        'type': 'folder',
                        'path': name
                    })
        except Exception as e:
            print(f'Error reading directory: {e}')

        return {
            'name': 'Storage',
            'type': 'folder',
            'contents': contents
        }

    def get_file_list(self, session_token=None):
        """Get a flat list of files for a session."""
        if session_token:
            session_path = os.path.join(self.base_path, session_token)
        else:
            session_path = self.base_path

        files = []
        if os.path.isdir(session_path):
            for name in sorted(os.listdir(session_path)):
                full_path = os.path.join(session_path, name)
                if os.path.isfile(full_path):
                    files.append({
                        'name': name,
                        'size': os.path.getsize(full_path),
                        'path': name
                    })
        return files

    def get_storage_stats(self, session_token=None):
        """Get storage usage stats for a session."""
        if session_token:
            session_path = os.path.join(self.base_path, session_token)
        else:
            session_path = self.base_path

        total_size = 0
        file_count = 0

        if os.path.isdir(session_path):
            for root, dirs, files in os.walk(session_path):
                for f in files:
                    fpath = os.path.join(root, f)
                    try:
                        total_size += os.path.getsize(fpath)
                        file_count += 1
                    except OSError:
                        pass

        return {
            'total_files': file_count,
            'total_size': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2)
        }
