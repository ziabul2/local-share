"""Device pairing and local network sync management."""

import secrets
import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, List

# Store paired devices: {pairing_token: {device_id, device_name, ip, port, paired_at, expires_at}}
PAIRED_DEVICES = {}

class PairingManager:
    """Manages device pairing, authentication tokens, and sync metadata."""
    
    def __init__(self, pairing_file: str = "paired_devices.json"):
        self.pairing_file = pairing_file
        self.load_pairings()
    
    def load_pairings(self):
        """Load paired devices from persistent storage."""
        global PAIRED_DEVICES
        if os.path.exists(self.pairing_file):
            try:
                with open(self.pairing_file, 'r') as f:
                    PAIRED_DEVICES = json.load(f)
            except Exception:
                PAIRED_DEVICES = {}
    
    def save_pairings(self):
        """Save paired devices to persistent storage."""
        try:
            with open(self.pairing_file, 'w') as f:
                json.dump(PAIRED_DEVICES, f, indent=2)
        except Exception as e:
            print(f"Failed to save pairings: {e}")
    
    def generate_pairing_token(self) -> str:
        """Generate a secure pairing token."""
        return secrets.token_urlsafe(24)
    
    def generate_device_id(self) -> str:
        """Generate a unique device ID."""
        return secrets.token_hex(8)
    
    def create_pairing_qr_data(self, local_ip: str, port: int, device_name: str = "PC") -> Dict:
        """
        Create pairing QR data with device info.
        Returns a dict with pairing info and a URL for the QR code.
        """
        pairing_token = self.generate_pairing_token()
        device_id = self.generate_device_id()
        
        pairing_data = {
            "type": "device_pairing",
            "version": "1.0",
            "device_id": device_id,
            "device_name": device_name,
            "ip": local_ip,
            "port": port,
            "pairing_token": pairing_token,
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(minutes=15)).isoformat(),
            "protocol": "https"  # Force HTTPS for security
        }
        
        # Store the pairing attempt
        PAIRED_DEVICES[pairing_token] = {
            "device_id": device_id,
            "device_name": device_name,
            "ip": local_ip,
            "port": port,
            "paired_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(days=30)).isoformat(),
            "status": "pending",  # pending -> confirmed after phone scan
            "synced_files": [],
            "last_sync": None
        }
        self.save_pairings()
        
        return pairing_data
    
    def get_pairing_qr_url(self, local_ip: str, port: int, device_name: str = "PC") -> tuple:
        """
        Generate a URL for the pairing QR code.
        When scanned, phone will open this URL and confirm pairing automatically.
        Returns (url, pairing_data)
        """
        pairing_data = self.create_pairing_qr_data(local_ip, port, device_name)
        
        # Create the pairing URL with URL parameters
        pairing_url = (
            f"https://{local_ip}:{port}/pair-confirm"
            f"?token={pairing_data['pairing_token']}"
            f"&device_id={pairing_data['device_id']}"
            f"&pc_name={device_name}"
            f"&created={pairing_data['created_at']}"
        )
        
        return pairing_url, pairing_data
    
    def verify_pairing_token(self, token: str) -> bool:
        """Verify if a pairing token is valid."""
        if token not in PAIRED_DEVICES:
            return False
        
        device = PAIRED_DEVICES[token]
        expires_at = datetime.fromisoformat(device['expires_at'])
        
        # Check expiration
        if datetime.now() > expires_at:
            del PAIRED_DEVICES[token]
            self.save_pairings()
            return False
        
        return True
    
    def confirm_pairing(self, token: str, phone_device_id: str, phone_device_name: str) -> bool:
        """
        Confirm a pairing from the phone side.
        Phone sends its device ID and name when confirming pairing.
        """
        if token not in PAIRED_DEVICES:
            return False
        
        device = PAIRED_DEVICES[token]
        device['status'] = 'confirmed'
        device['phone_device_id'] = phone_device_id
        device['phone_device_name'] = phone_device_name
        device['confirmed_at'] = datetime.now().isoformat()
        device['active'] = True
        device['last_seen'] = datetime.now().isoformat()
        self.save_pairings()
        return True
    
    def get_paired_devices(self) -> List[Dict]:
        """Get list of all confirmed paired devices."""
        return [
            dev for token, dev in PAIRED_DEVICES.items()
            if dev.get('status') == 'confirmed'
        ]
    
    def get_device_by_token(self, token: str) -> Optional[Dict]:
        """Get device info by pairing token."""
        return PAIRED_DEVICES.get(token)
    
    def update_sync_info(self, token: str, files: List[Dict]):
        """Update sync metadata for a paired device."""
        if token in PAIRED_DEVICES:
            PAIRED_DEVICES[token]['synced_files'] = files
            PAIRED_DEVICES[token]['last_sync'] = datetime.now().isoformat()
            self.save_pairings()
    
    def revoke_pairing(self, token: str) -> bool:
        """Revoke a device pairing."""
        if token in PAIRED_DEVICES:
            del PAIRED_DEVICES[token]
            self.save_pairings()
            return True
        return False
    
    def update_device_activity(self, token: str) -> bool:
        """Update last_seen timestamp for a device."""
        if token in PAIRED_DEVICES:
            PAIRED_DEVICES[token]['last_seen'] = datetime.now().isoformat()
            PAIRED_DEVICES[token]['active'] = True
            self.save_pairings()
            return True
        return False
    
    def get_device_stats(self, token: str) -> Dict:
        """Get photo/video counts and stats for a device."""
        if token not in PAIRED_DEVICES:
            return {}
        
        device = PAIRED_DEVICES[token]
        
        # Count photos and videos from uploads directory
        upload_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads', token)
        photo_count = 0
        video_count = 0
        total_size = 0
        
        if os.path.isdir(upload_path):
            for fname in os.listdir(upload_path):
                fpath = os.path.join(upload_path, fname)
                if os.path.isfile(fpath):
                    ext = os.path.splitext(fname)[1].lower()
                    total_size += os.path.getsize(fpath)
                    
                    if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.heic', '.heif']:
                        photo_count += 1
                    elif ext in ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.m4v', '.3gp']:
                        video_count += 1
        
        # Check if device is active (seen within last 5 minutes)
        last_seen = device.get('last_seen')
        is_active = False
        if last_seen:
            last_seen_dt = datetime.fromisoformat(last_seen)
            is_active = (datetime.now() - last_seen_dt).total_seconds() < 300  # 5 minutes
        
        return {
            'token': token,
            'device_name': device.get('phone_device_name', 'Unknown Device'),
            'status': device.get('status', 'pending'),
            'active': is_active,
            'photo_count': photo_count,
            'video_count': video_count,
            'total_files': photo_count + video_count,
            'total_size': total_size,
            'last_seen': last_seen,
            'last_sync': device.get('last_sync'),
            'paired_at': device.get('confirmed_at', device.get('paired_at'))
        }
    
    def get_all_devices_with_stats(self) -> List[Dict]:
        """Get all devices with real-time stats."""
        devices_with_stats = []
        for token, device in PAIRED_DEVICES.items():
            if device.get('status') == 'confirmed':
                stats = self.get_device_stats(token)
                devices_with_stats.append(stats)
        return devices_with_stats
    
    def cleanup_inactive_devices(self, inactive_days: int = 30) -> int:
        """Remove devices that haven't been active for specified days."""
        removed_count = 0
        tokens_to_remove = []
        
        for token, device in PAIRED_DEVICES.items():
            last_seen = device.get('last_seen')
            if last_seen:
                try:
                    last_seen_dt = datetime.fromisoformat(last_seen)
                    days_inactive = (datetime.now() - last_seen_dt).total_seconds() / 86400
                    
                    if days_inactive > inactive_days:
                        tokens_to_remove.append(token)
                except Exception:
                    pass  # Invalid date format
        
        # Remove inactive devices
        for token in tokens_to_remove:
            del PAIRED_DEVICES[token]
            removed_count += 1
        
        if removed_count > 0:
            self.save_pairings()
        
        return removed_count


# Global instance
pairing_manager = PairingManager()
