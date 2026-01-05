"""Phone Storage Educator - Flask Backend with Local Network Sync."""

from flask import Flask, render_template, request, jsonify
import base64
import socket
import secrets
import os
import sys
import logging
import json

# Suppress Flask startup messages
logging.getLogger('werkzeug').setLevel(logging.ERROR)

# Add parent dir to path to import qr_generator
# This script may be run from project root (python backend/app.py)
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
from qr_generator import generate_qr_png_bytes

# Import API blueprint (use absolute import for direct script execution)
try:
    from backend.api import api_bp
except ImportError:
    from api import api_bp

# Import pairing manager for device pairing and local network sync
try:
    from backend.pairing import pairing_manager
except ImportError:
    from pairing import pairing_manager

app = Flask(
    __name__,
    static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static'),
    template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')
)

# Register API blueprint
app.register_blueprint(api_bp)

# runtime session token and qr data
SESSION_TOKEN = None
QR_DATA_URL = None
UPLOAD_ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(UPLOAD_ROOT, exist_ok=True)

# Track all sessions
SESSIONS = {}  # {token: {granted: bool, created_at: timestamp, files: [...]}


def get_local_ip() -> str:
    """Return a likely local IP address; fallback to '0.0.0.0' on error."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "0.0.0.0"


@app.route("/")
def index():
    """Main landing page with QR code for session scanning."""
    return render_template("index.html", qr_data_url=QR_DATA_URL)


@app.route('/session/<token>')
def session_page(token: str):
    """Learning paths page after QR scan."""
    if token != SESSION_TOKEN:
        return jsonify({'error': 'invalid session'}), 404
    return render_template('session.html', token=token)


@app.route('/storage/<token>')
def storage_page(token: str):
    """Storage simulator page."""
    if token != SESSION_TOKEN:
        return jsonify({'error': 'invalid session'}), 404
    return render_template('simulator.html', token=token)


@app.route('/permissions/<token>')
def permissions_page(token: str):
    """Permissions education page."""
    if token != SESSION_TOKEN:
        return jsonify({'error': 'invalid session'}), 404
    return render_template('permissions.html', token=token)


@app.route('/camera/<token>')
def camera_page(token: str):
    """Camera and file storage page."""
    if token != SESSION_TOKEN:
        return jsonify({'error': 'invalid session'}), 404
    return render_template('camera.html', token=token)


@app.route('/explorer/<token>')
def explorer_page(token: str):
    """File explorer for accessing phone storage and gallery."""
    return render_template('explorer.html', token=token)


@app.route('/admin')
def admin_page():
    """Admin panel showing all sessions."""
    return render_template('admin.html')


@app.route('/generate', methods=['POST'])
def generate_qr():
    """Generate QR code endpoint (legacy, for main page QR maker)."""
    payload = request.get_json(force=True) or {}
    text = payload.get("text", "")
    size = payload.get("size", None)
    try:
        box_size = int(size) if size is not None else 10
    except Exception:
        box_size = 10
    box_size = max(1, min(box_size, 40))

    if not text:
        return jsonify({"error": "no text provided"}), 400

    try:
        img_bytes = generate_qr_png_bytes(text, box_size=box_size)
    except Exception as exc:
        return jsonify({"error": "failed to generate QR", "detail": str(exc)}), 500

    data_url = "data:image/png;base64," + base64.b64encode(img_bytes).decode("ascii")
    return jsonify({"data_url": data_url})


@app.route('/api/session/grant/<token>', methods=['POST'])
def grant_permission(token: str):
    """Mark a session as granted permission."""
    if token not in SESSIONS:
        SESSIONS[token] = {'granted': False, 'created_at': secrets.token_urlsafe(4), 'files': []}
    SESSIONS[token]['granted'] = True
    return jsonify({'ok': True})


@app.route('/api/admin/sessions', methods=['GET'])
def admin_sessions():
    """Get all sessions with their file data."""
    sessions_data = []
    for token, session in SESSIONS.items():
        files = []
        session_path = os.path.join(UPLOAD_ROOT, token)
        if os.path.isdir(session_path):
            for fname in os.listdir(session_path):
                fpath = os.path.join(session_path, fname)
                if os.path.isfile(fpath):
                    files.append({
                        'name': fname,
                        'size': os.path.getsize(fpath)
                    })
        
        sessions_data.append({
            'token': token,
            'granted': session.get('granted', False),
            'created_at': session.get('created_at', ''),
            'files': files,
            'file_count': len(files)
        })
    
    return jsonify({'sessions': sessions_data})


@app.route('/api/admin/paired-devices', methods=['GET'])
def admin_paired_devices():
    """Get all paired devices with real-time statistics."""
    devices = pairing_manager.get_all_devices_with_stats()
    
    # Calculate summary statistics
    total_devices = len(devices)
    active_devices = sum(1 for d in devices if d.get('active', False))
    total_photos = sum(d.get('photo_count', 0) for d in devices)
    total_videos = sum(d.get('video_count', 0) for d in devices)
    total_files = sum(d.get('total_files', 0) for d in devices)
    
    return jsonify({
        'devices': devices,
        'summary': {
            'total_devices': total_devices,
            'active_devices': active_devices,
            'total_photos': total_photos,
            'total_videos': total_videos,
            'total_files': total_files
        }
    })


@app.route('/api/gallery/<token>', methods=['GET'])
def get_gallery(token: str):
    """Get gallery files for a session."""
    session_path = os.path.join(UPLOAD_ROOT, token)
    gallery_files = []
    
    if os.path.isdir(session_path):
        for fname in os.listdir(session_path):
            fpath = os.path.join(session_path, fname)
            if os.path.isfile(fpath):
                # Check if it's an image or video
                ext = os.path.splitext(fname)[1].lower()
                if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
                    gallery_files.append({
                        'name': fname,
                        'type': 'image',
                        'path': f'/uploads/{token}/{fname}',
                        'size': os.path.getsize(fpath)
                    })
                elif ext in ['.mp4', '.avi', '.mov', '.mkv', '.webm']:
                    gallery_files.append({
                        'name': fname,
                        'type': 'video',
                        'path': f'/uploads/{token}/{fname}',
                        'size': os.path.getsize(fpath)
                    })
    
    return jsonify({'gallery': gallery_files})


# ===== Local Network Sync & Device Pairing Routes =====

@app.route('/pairing', methods=['GET'])
def pairing_page():
    """Page showing device pairing QR code for local network sync."""
    return render_template('pairing.html')


@app.route('/pair-confirm', methods=['GET'])
def pair_confirm_page():
    """Phone confirmation page for device pairing."""
    return render_template('pair-confirm.html')


@app.route('/api/pairing/generate', methods=['POST'])
def generate_pairing_qr():
    """
    Generate a pairing QR code for local network device sync.
    Phone scans this QR to pair with the PC.
    QR contains a URL that auto-redirects to pair-confirm page.
    """
    local_ip = get_local_ip()
    port = 5000  # Assuming Flask runs on 5000
    device_name = request.json.get('device_name', 'My PC') if request.json else 'My PC'
    
    # Generate pairing URL and data
    pairing_url, pairing_data = pairing_manager.get_pairing_qr_url(local_ip, port, device_name)
    
    # Generate QR code from the URL (not JSON)
    # When scanned on phone, this URL opens directly in browser
    img_bytes = generate_qr_png_bytes(pairing_url)
    qr_data_url = "data:image/png;base64," + base64.b64encode(img_bytes).decode("ascii")
    
    return jsonify({
        'qr_data_url': qr_data_url,
        'pairing_url': pairing_url,
        'pairing_token': pairing_data['pairing_token'],
        'device_id': pairing_data['device_id'],
        'pairing_data': pairing_data
    })


@app.route('/api/pairing/confirm', methods=['POST'])
def confirm_pairing():
    """
    Confirm device pairing from phone side.
    Phone sends pairing token, its device ID and name.
    """
    data = request.get_json()
    pairing_token = data.get('pairing_token')
    phone_device_id = data.get('phone_device_id')
    phone_device_name = data.get('phone_device_name', 'Phone')
    
    if not pairing_token or not pairing_manager.verify_pairing_token(pairing_token):
        return jsonify({'error': 'invalid or expired pairing token'}), 401
    
    success = pairing_manager.confirm_pairing(pairing_token, phone_device_id, phone_device_name)
    
    if success:
        return jsonify({
            'ok': True,
            'message': f'Device "{phone_device_name}" paired successfully',
            'pairing_token': pairing_token
        })
    else:
        return jsonify({'error': 'Failed to confirm pairing'}), 400


@app.route('/api/pairing/devices', methods=['GET'])
def get_paired_devices():
    """Get list of all paired devices on local network."""
    devices = pairing_manager.get_paired_devices()
    return jsonify({'devices': devices})


@app.route('/api/pairing/revoke/<token>', methods=['POST'])
def revoke_pairing(token: str):
    """Revoke a device pairing."""
    if pairing_manager.revoke_pairing(token):
        return jsonify({'ok': True, 'message': 'Pairing revoked'})
    else:
        return jsonify({'error': 'Pairing not found'}), 404


@app.route('/api/sync/<token>', methods=['POST'])
def sync_files(token: str):
    """
    Sync files from paired device.
    Receives list of files from phone and stores them.
    """
    if not pairing_manager.verify_pairing_token(token):
        return jsonify({'error': 'invalid pairing token'}), 401
    
    data = request.get_json()
    files = data.get('files', [])
    
    # Update sync info
    pairing_manager.update_sync_info(token, files)
    
    return jsonify({
        'ok': True,
        'synced': len(files),
        'message': f'Synced {len(files)} files from paired device'
    })


@app.route('/api/admin/cleanup-inactive', methods=['POST'])
def cleanup_inactive_devices():
    """Remove devices inactive for more than specified days (default: 30)."""
    data = request.get_json() or {}
    days = data.get('days', 30)  # Default 30 days
    
    removed_count = pairing_manager.cleanup_inactive_devices(days)
    
    return jsonify({
        'ok': True,
        'removed': removed_count,
        'message': f'Removed {removed_count} inactive device(s)'
    })


if __name__ == "__main__":
    # create a per-run session token and generate a QR that points to the session URL
    local_ip = get_local_ip()
    host = local_ip if local_ip != "0.0.0.0" else "0.0.0.0"
    SESSION_TOKEN = secrets.token_urlsafe(16)
    
    # Initialize session in SESSIONS dict
    import datetime
    SESSIONS[SESSION_TOKEN] = {
        'granted': False,
        'created_at': datetime.datetime.now().isoformat(),
        'files': []
    }
    
    # build a URL that the phone should open when scanning
    session_url = f"http://{local_ip}:5000/session/{SESSION_TOKEN}"
    # generate QR data url for embedding in the desktop page
    img_bytes = generate_qr_png_bytes(session_url)
    QR_DATA_URL = "data:image/png;base64," + base64.b64encode(img_bytes).decode("ascii")

    # write values into app global namespace so routes see them
    globals()['SESSION_TOKEN'] = SESSION_TOKEN
    globals()['QR_DATA_URL'] = QR_DATA_URL

    # Suppress Flask startup messages
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    
    # Try to enable TLS
    cert_file, key_file = None, None
    try:
        from backend.tls_setup import generate_self_signed_cert
    except ImportError:
        from tls_setup import generate_self_signed_cert
    
    try:
        cert_file, key_file = generate_self_signed_cert("certs", common_name=local_ip)
        print(f"\n✓ HTTPS enabled for local network access at https://{local_ip}:5000")
        ssl_context = (cert_file, key_file)
    except Exception as e:
        print(f"⚠ TLS setup failed: {e}")
        print(f"Falling back to HTTP on http://{local_ip}:5000")
        ssl_context = None
    
    print(f"\nQR Pairing endpoint available at:")
    print(f"  - http://{local_ip}:5000/pairing")
    print(f"  - https://{local_ip}:5000/pairing (if TLS available)")
    print(f"\nSession URL: {session_url}")
    print(f"\n🐛 Debug mode: ENABLED")
    print(f"🔄 Auto-reload: ENABLED\n")
    
    # Run with debug mode enabled for better development experience
    app.run(host=host, port=5000, debug=True, use_reloader=True, ssl_context=ssl_context)
