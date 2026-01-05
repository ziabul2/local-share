"""Photo and gallery management utilities."""

import os
import mimetypes
from typing import List, Dict, Optional
from pathlib import Path


class PhotoGalleryManager:
    """Manage photo uploads, gallery display, and metadata."""
    
    # Supported media types
    IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg'}
    VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv'}
    MEDIA_EXTENSIONS = IMAGE_EXTENSIONS | VIDEO_EXTENSIONS
    
    @staticmethod
    def is_media_file(filename: str) -> bool:
        """Check if file is an image or video."""
        ext = os.path.splitext(filename)[1].lower()
        return ext in PhotoGalleryManager.MEDIA_EXTENSIONS
    
    @staticmethod
    def get_media_type(filename: str) -> Optional[str]:
        """Get media type: 'image', 'video', or None."""
        ext = os.path.splitext(filename)[1].lower()
        
        if ext in PhotoGalleryManager.IMAGE_EXTENSIONS:
            return 'image'
        elif ext in PhotoGalleryManager.VIDEO_EXTENSIONS:
            return 'video'
        return None
    
    @staticmethod
    def get_file_info(filepath: str, rel_path: str = None) -> Optional[Dict]:
        """Get file metadata for gallery display."""
        if not os.path.isfile(filepath):
            return None
        
        filename = os.path.basename(filepath)
        media_type = PhotoGalleryManager.get_media_type(filename)
        
        if not media_type:
            return None
        
        try:
            file_size = os.path.getsize(filepath)
            file_stat = os.stat(filepath)
            
            return {
                'name': filename,
                'type': media_type,
                'size': file_size,
                'path': rel_path or f'/uploads/{filename}',
                'modified': file_stat.st_mtime,
                'mime_type': mimetypes.guess_type(filepath)[0] or 'application/octet-stream'
            }
        except Exception as e:
            print(f"Error getting file info for {filepath}: {e}")
            return None
    
    @staticmethod
    def scan_directory(directory: str, token: str = None) -> List[Dict]:
        """
        Scan directory for media files and return gallery list.
        
        Args:
            directory: Directory path to scan
            token: Optional session token for path construction
            
        Returns:
            List of media file dictionaries
        """
        gallery = []
        
        if not os.path.isdir(directory):
            return gallery
        
        try:
            for filename in sorted(os.listdir(directory)):
                filepath = os.path.join(directory, filename)
                
                if not os.path.isfile(filepath):
                    continue
                
                media_type = PhotoGalleryManager.get_media_type(filename)
                if not media_type:
                    continue
                
                file_size = os.path.getsize(filepath)
                rel_path = f'/uploads/{token}/{filename}' if token else f'/uploads/{filename}'
                
                gallery.append({
                    'name': filename,
                    'type': media_type,
                    'size': file_size,
                    'path': rel_path
                })
        
        except Exception as e:
            print(f"Error scanning directory {directory}: {e}")
        
        return gallery
    
    @staticmethod
    def organize_by_date(files: List[Dict]) -> Dict[str, List[Dict]]:
        """Organize files by month for better gallery display."""
        organized = {}
        
        for file in files:
            # Extract date from filename if possible (e.g., IMG_20250122_143022.jpg)
            name = file['name']
            
            # Try to parse date from common formats
            date_str = None
            if '_' in name and len(name.split('_')[1]) >= 8:
                date_str = name.split('_')[1][:8]  # YYYYMMDD
            
            if date_str:
                # Format as YYYY-MM
                month_key = f"{date_str[:4]}-{date_str[4:6]}"
            else:
                month_key = "Other"
            
            if month_key not in organized:
                organized[month_key] = []
            
            organized[month_key].append(file)
        
        return organized
    
    @staticmethod
    def sort_by_date(files: List[Dict], reverse: bool = True) -> List[Dict]:
        """
        Sort files by name (which often contains date info).
        
        Args:
            files: List of file dictionaries
            reverse: If True, sort newest first
            
        Returns:
            Sorted list
        """
        return sorted(files, key=lambda f: f['name'], reverse=reverse)
    
    @staticmethod
    def filter_by_type(files: List[Dict], media_type: str) -> List[Dict]:
        """Filter files by type (image or video)."""
        return [f for f in files if f['type'] == media_type]
    
    @staticmethod
    def get_stats(files: List[Dict]) -> Dict:
        """Get gallery statistics."""
        images = PhotoGalleryManager.filter_by_type(files, 'image')
        videos = PhotoGalleryManager.filter_by_type(files, 'video')
        
        total_size = sum(f['size'] for f in files)
        
        return {
            'total_files': len(files),
            'image_count': len(images),
            'video_count': len(videos),
            'total_size': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2)
        }
    
    @staticmethod
    def generate_thumbnail_path(filepath: str) -> str:
        """Generate thumbnail filename for a media file."""
        name, ext = os.path.splitext(filepath)
        return f"{name}_thumb.jpg"
    
    @staticmethod
    def get_download_filename(filename: str, token: str) -> str:
        """Generate safe download filename with token prefix."""
        # Sanitize and add token for uniqueness
        safe_name = "".join(c for c in filename if c.isalnum() or c in '._-')
        return f"{token[:8]}_{safe_name}"


class UploadManager:
    """Manage file uploads and storage."""
    
    @staticmethod
    def get_upload_dir(token: str, base_dir: str = "uploads") -> str:
        """Get or create upload directory for token."""
        upload_dir = os.path.join(base_dir, token)
        os.makedirs(upload_dir, exist_ok=True)
        return upload_dir
    
    @staticmethod
    def get_upload_path(token: str, filename: str, base_dir: str = "uploads") -> str:
        """Get full path for uploaded file."""
        upload_dir = UploadManager.get_upload_dir(token, base_dir)
        return os.path.join(upload_dir, filename)
    
    @staticmethod
    def cleanup_old_uploads(base_dir: str = "uploads", days: int = 30) -> int:
        """
        Remove upload directories older than specified days.
        
        Returns:
            Number of directories cleaned up
        """
        import time
        cleaned = 0
        cutoff_time = time.time() - (days * 24 * 60 * 60)
        
        if not os.path.isdir(base_dir):
            return 0
        
        try:
            for token_dir in os.listdir(base_dir):
                dir_path = os.path.join(base_dir, token_dir)
                
                if not os.path.isdir(dir_path):
                    continue
                
                dir_mtime = os.path.getmtime(dir_path)
                
                if dir_mtime < cutoff_time:
                    try:
                        import shutil
                        shutil.rmtree(dir_path)
                        cleaned += 1
                    except Exception as e:
                        print(f"Could not remove {dir_path}: {e}")
        
        except Exception as e:
            print(f"Error cleaning up old uploads: {e}")
        
        return cleaned
    
    @staticmethod
    def get_directory_size(directory: str) -> int:
        """Get total size of directory in bytes."""
        total = 0
        try:
            for dirpath, dirnames, filenames in os.walk(directory):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if os.path.isfile(filepath):
                        total += os.path.getsize(filepath)
        except Exception:
            pass
        
        return total
    
    @staticmethod
    def format_size(bytes: int) -> str:
        """Format bytes as human-readable string."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes < 1024:
                return f"{bytes:.1f}{unit}"
            bytes /= 1024
        return f"{bytes:.1f}TB"


# Example usage in Flask
if __name__ == "__main__":
    # Scan gallery
    gallery = PhotoGalleryManager.scan_directory("uploads/test_token", "test_token")
    print(f"Found {len(gallery)} media files")
    
    # Get stats
    stats = PhotoGalleryManager.get_stats(gallery)
    print(f"Stats: {stats}")
    
    # Organize by date
    organized = PhotoGalleryManager.organize_by_date(gallery)
    print(f"Organized into {len(organized)} months")
    
    # Filter
    images = PhotoGalleryManager.filter_by_type(gallery, 'image')
    print(f"Images: {len(images)}")
