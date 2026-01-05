# Phone Storage Educator - Implementation Complete

## What's Been Built

A complete educational web app that teaches mobile storage and permissions through hands-on learning:

### Desktop Side
- **QR Generator**: Create custom QR codes
- **Automatic Session QR**: Generates a unique QR every time the app starts pointing to a learning session

### Mobile Side (After Scanning QR)
- **Permission Request**: Asks for camera + storage access with clear, educational messaging
- **Camera Section**: Live video feed with photo capture capability
- **File Manager**: Upload files, view storage stats, download files
- **Educational Content**: Learn about Android/iOS permissions and security best practices

---

## Project Structure

```
phone-storage-educator/
├── backend/
│   ├── app.py                    # Flask server (main entry point)
│   ├── storage.py                # File storage simulator class
│   ├── permissions_manager.py    # Permission documentation & education
│   ├── api/
│   │   └── __init__.py          # REST API endpoints
│   └── __init__.py
├── frontend/
│   ├── index.html               # Main QR generator + session QR display
│   ├── session.html             # Learning paths selector
│   ├── camera.html              # Camera & file management (NEW)
│   ├── permissions.html         # Permissions education
│   ├── simulator.html           # Storage explorer (legacy)
│   └── components/              # Reserved for UI components
├── static/
│   ├── css/style.css           # Modern 3D floating UI theme
│   └── js/
│       ├── main.js             # QR generator logic
│       ├── camera.js           # Camera + file integration (NEW)
│       ├── session.js          # Session flow logic
│       ├── permissions.js      # Permission education UI
│       └── simulator.js        # Storage explorer logic
├── qr_generator.py             # QR code utility
├── requirements.txt            # Python dependencies
├── run.bat                      # Windows one-click launcher
├── README.md                    # Project documentation
└── USER_FLOW.md               # Complete user journey guide
```

---

## Key Features

### 1. Automatic Session QR (Desktop)
```
http://localhost:5000/
    ↓
Displays QR code pointing to: http://192.168.100.7:5000/session/<unique-token>
```

### 2. Permission Request (Mobile)
```
Scan QR → /session/<token>
    ↓
Click "📷 Camera & Files"
    ↓
/camera/<token>
    ↓
Permission Modal appears
    ↓
User grants camera + storage access
```

### 3. Camera & File Interface
- **Live camera feed** with capture button
- **Photo gallery** with download/delete options
- **File uploader** with drag-and-drop
- **File browser** with real-time updates

### 4. Educational Resources
- **Permissions guide** for Android/iOS
- **Security tips** for mobile devices
- **Interactive learning** with real file/camera access

---

## How to Launch

### Option 1: One-Click (Windows)
```powershell
# Just double-click run.bat in the project folder
run.bat
```

### Option 2: Manual (Windows PowerShell)
```powershell
# Activate venv
venv\Scripts\Activate.ps1

# Go to backend
cd backend

# Run Flask
python app.py
```

### Option 3: Manual (Linux/Mac)
```bash
source venv/bin/activate
cd backend
python app.py
```

---

## Access URLs

Once running (server on 192.168.100.7):

- **Desktop QR Generator**: http://localhost:5000 or http://192.168.100.7:5000
- **Mobile Learning**: Scan the QR code displayed on desktop
- **Session URL**: http://192.168.100.7:5000/session/<token> (each session unique)
- **Camera Page**: http://192.168.100.7:5000/camera/<token>

---

## Technical Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Camera API**: `navigator.mediaDevices.getUserMedia` (browser native)
- **QR Codes**: `qrcode` + `Pillow` Python libraries
- **File Storage**: Local filesystem (in `uploads/` directory)
- **Styling**: Modern 3D floating card UI with glassmorphism

---

## What Students Learn

1. **File System Navigation** - Understand device storage structure
2. **Permission Concepts** - Why apps request access to camera/storage
3. **Security Awareness** - Which permissions are dangerous
4. **Data Privacy** - How to manage app permissions safely
5. **Hands-On Experience** - Real camera capture and file management

---

## API Endpoints

All endpoints require a valid session token in the URL:

### Storage API
- `GET /api/storage/list/<token>` - List files
- `POST /api/storage/upload/<token>` - Upload file
- `GET /api/storage/download/<token>/<filename>` - Download file
- `GET /api/storage/stats/<token>` - Storage statistics
- `GET /api/storage/structure/<token>` - Directory structure

### Permissions API
- `GET /api/permissions/tips` - Security tips
- `GET /api/permissions/dangerous?platform=android` - Dangerous permissions
- `GET /api/permissions/detail/<name>?platform=android` - Permission details
- `GET /api/permissions/all?platform=android` - All permissions

---

## Session Management

- **Token Generation**: Unique 16-character random token per app start
- **Token Location**: Generated at startup, passed to frontend via template variable
- **Persistence**: Files stored in `uploads/<token>/` directory
- **Cleanup**: Cleared on app restart (no persistence by design for privacy)

---

## Browser Compatibility

- **Camera API**: Requires HTTPS or localhost (works fine locally)
- **Storage API**: Works on all modern browsers
- **Tested On**: Chrome, Edge, Safari, Firefox (on mobile)

---

## For Teachers

1. Start app with `run.bat`
2. Point projector/screen at desktop showing QR
3. Students scan with their phones
4. Each gets a unique session - no data shared between students
5. Perfect for teaching mobile privacy and permissions

---

## Next Steps (Optional Enhancements)

- [ ] Add WebSocket for real-time file sync
- [ ] Session expiry (tokens valid for X minutes)
- [ ] Two-factor permission confirmation
- [ ] Dark mode toggle
- [ ] Export session data (learning analytics)
- [ ] Docker containerization
- [ ] Deployment to cloud (Heroku, AWS, etc.)

---

## Support & Troubleshooting

**Camera not working?**
- Ensure browser has permission to access camera
- Try a different browser (Chrome recommended)
- Check that you're using http://localhost:5000 or proper local IP

**File upload failing?**
- Check that the server is running
- Verify session token in URL is valid
- Try refreshing the page

**QR code not displaying?**
- Restart the server
- Clear browser cache
- Try accessing main page directly (http://localhost:5000)

---

## Deployment Notes

For production use, replace Flask's development server with:
- **Gunicorn** (Linux/Mac): `pip install gunicorn && gunicorn -w 4 -b 0.0.0.0:5000 app:app`
- **Waitress** (Windows): `pip install waitress && waitress-serve --port=5000 app:app`
- **Docker**: Create a Dockerfile to containerize the app

---

**Ready to educate! 🚀**
