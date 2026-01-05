"""REST API endpoints for storage, permissions, and QR functionality."""

from flask import Blueprint, jsonify, request, send_from_directory, abort, url_for
from werkzeug.utils import secure_filename
import os

from ..storage import StorageSimulator
from ..permissions_manager import PermissionsManager

api_bp = Blueprint('api', __name__, url_prefix='/api')
storage = StorageSimulator()


@api_bp.route('/storage/list/<token>', methods=['GET'])
def list_storage(token):
    """List files in storage for a session."""
    files = storage.get_file_list(session_token=token)
    return jsonify({'files': files})


@api_bp.route('/storage/structure/<token>', methods=['GET'])
def get_storage_structure(token):
    """Get complete directory structure for a session."""
    struct = storage.get_directory_structure(session_token=token)
    return jsonify(struct)


@api_bp.route('/storage/stats/<token>', methods=['GET'])
def get_storage_stats(token):
    """Get storage usage statistics for a session."""
    stats = storage.get_storage_stats(session_token=token)
    return jsonify(stats)


@api_bp.route('/storage/upload/<token>', methods=['POST'])
def upload_file(token):
    """Upload a file to a session."""
    if 'file' not in request.files:
        return jsonify({'error': 'no file part'}), 400
    f = request.files['file']
    if f.filename == '':
        return jsonify({'error': 'no selected file'}), 400

    fname = secure_filename(f.filename)
    dest_dir = os.path.join(storage.base_path, token)
    os.makedirs(dest_dir, exist_ok=True)
    dest_path = os.path.join(dest_dir, fname)
    f.save(dest_path)
    
    # Track file in SESSIONS
    from ..app import SESSIONS
    if token not in SESSIONS:
        SESSIONS[token] = {'granted': False, 'created_at': '', 'files': []}
    SESSIONS[token]['files'].append({'name': fname, 'size': os.path.getsize(dest_path)})
    
    # Update device activity if this is a pairing token
    try:
        from ..pairing import pairing_manager
        pairing_manager.update_device_activity(token)
    except Exception:
        pass  # Not a pairing token or error updating activity
    
    return jsonify({'ok': True, 'filename': fname})


@api_bp.route('/storage/download/<token>/<filename>', methods=['GET'])
def download_file(token, filename):
    """Download a file from a session."""
    session_path = os.path.join(storage.base_path, token)
    if not os.path.isdir(session_path):
        abort(404)
    return send_from_directory(session_path, secure_filename(filename))


@api_bp.route('/permissions/all', methods=['GET'])
def get_all_permissions():
    """Get all documented permissions."""
    platform = request.args.get('platform', 'android')
    perms = PermissionsManager.get_all_permissions()
    return jsonify(perms.get(platform, {}))


@api_bp.route('/permissions/dangerous', methods=['GET'])
def get_dangerous_permissions():
    """Get dangerous/sensitive permissions for education."""
    platform = request.args.get('platform', 'android')
    perms = PermissionsManager.get_dangerous_permissions(platform=platform)
    return jsonify(perms)


@api_bp.route('/permissions/tips', methods=['GET'])
def get_security_tips():
    """Get security tips about permissions and storage."""
    tips = PermissionsManager.get_security_tips()
    return jsonify({'tips': tips})


@api_bp.route('/permissions/detail/<permission>', methods=['GET'])
def get_permission_detail(permission):
    """Get detailed info about a specific permission."""
    platform = request.args.get('platform', 'android')
    perm = PermissionsManager.get_permission(permission, platform=platform)
    if not perm:
        return jsonify({'error': 'permission not found'}), 404
    return jsonify(perm)
