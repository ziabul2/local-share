from flask import Flask, render_template, request, jsonify, send_from_directory, abort, url_for
from generate_qr import generate_qr_png_bytes
import base64
import socket
import secrets
import os
from werkzeug.utils import secure_filename


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


app = Flask(__name__, static_folder="static", template_folder="templates")

# runtime session token and qr data
SESSION_TOKEN = None
QR_DATA_URL = None
UPLOAD_ROOT = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_ROOT, exist_ok=True)


@app.route("/")
def index():
    # show the QR generated at server start so the phone can scan it
    return render_template("index.html", qr_data_url=QR_DATA_URL)


@app.route('/session/<token>')
def session_page(token: str):
    if token != SESSION_TOKEN:
        abort(404)
    return render_template('session.html', token=token)


@app.route('/upload/<token>', methods=['POST'])
def upload_file(token: str):
    if token != SESSION_TOKEN:
        return jsonify({'error': 'invalid session token'}), 403
    if 'file' not in request.files:
        return jsonify({'error': 'no file part'}), 400
    f = request.files['file']
    if f.filename == '':
        return jsonify({'error': 'no selected file'}), 400
    fname = secure_filename(f.filename)
    dest_dir = os.path.join(UPLOAD_ROOT, token)
    os.makedirs(dest_dir, exist_ok=True)
    dest_path = os.path.join(dest_dir, fname)
    f.save(dest_path)
    return jsonify({'ok': True, 'filename': fname})


@app.route('/uploads/<token>/<path:filename>')
def serve_upload(token: str, filename: str):
    if token != SESSION_TOKEN:
        abort(404)
    return send_from_directory(os.path.join(UPLOAD_ROOT, token), filename)


@app.route('/poll/<token>')
def poll_files(token: str):
    if token != SESSION_TOKEN:
        return jsonify({'files': []})
    d = os.path.join(UPLOAD_ROOT, token)
    files = []
    if os.path.isdir(d):
        for name in sorted(os.listdir(d)):
            files.append({'name': name, 'url': url_for('serve_upload', token=token, filename=name)})
    return jsonify({'files': files})


@app.route("/generate", methods=["POST"])
def generate():
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


if __name__ == "__main__":
    # create a per-run session token and generate a QR that points to the session URL
    local_ip = get_local_ip()
    host = local_ip if local_ip != "0.0.0.0" else "0.0.0.0"
    SESSION_TOKEN = secrets.token_urlsafe(16)
    # build a URL that the phone should open when scanning
    session_url = f"http://{local_ip}:5000/session/{SESSION_TOKEN}"
    # generate QR data url for embedding in the desktop page
    img_bytes = generate_qr_png_bytes(session_url)
    QR_DATA_URL = "data:image/png;base64," + base64.b64encode(img_bytes).decode("ascii")

    # write values into app global namespace so routes see them
    globals()['SESSION_TOKEN'] = SESSION_TOKEN
    globals()['QR_DATA_URL'] = QR_DATA_URL

    # Run without debug to avoid printing Werkzeug dev link/pin
    app.run(host=host, port=5000, debug=False, use_reloader=False)
