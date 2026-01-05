# Phone Storage Educator - User Flow

## Complete Learning Journey

### Desktop (Teacher / Setup)

1. **Open http://localhost:5000 or http://192.168.100.7:5000**
   - Shows main QR Generator interface
   - Can create custom QR codes to learn
   - **Automatically displays a Session QR Code** that points to `/session/<unique-token>`

### Mobile (Student / Learning)

#### Step 1: Scan QR Code
- User scans the automatically-generated session QR from the desktop
- Redirected to `http://192.168.100.7:5000/session/<token>`
- Sees "Learning Paths" page with two buttons:
  - **📷 Camera & Files** ← Main learning path (requests permissions)
  - **🔒 Learn Permissions** ← Educational resource

#### Step 2: Request Permissions
- Click "📷 Camera & Files" → `/camera/<token>`
- Permission Modal appears:
  - "This app needs access to your camera and storage"
  - **[Grant Access]** button
  - **[Skip for Now]** button

#### Step 3: Camera & File Storage
Once in the camera section, user sees:

**Camera Section:**
- Live video feed from device camera
- 📸 **Capture** button → takes photos
- **Stop Camera** button → stops the feed

**Captured Photos:**
- Grid of captured photos
- Click to download as JPEG
- **Del** button to remove

**File Upload:**
- File picker input
- **Upload** button → uploads to session storage

**File Browser:**
- Lists uploaded files with sizes
- **Download** links to access files
- **Refresh** button to update
- **Back** button to return to learning paths

#### Step 4: Permissions Learning (Optional)
- Click "🔒 Learn Permissions" → `/permissions/<token>`
- Learn about:
  - **Dangerous/Sensitive Permissions**
  - Platform-specific (Android/iOS)
  - Educational points for each
  - Security tips

---

## Technical Flow

```
Desktop: http://localhost:5000/
    ↓
    [Shows QR: http://192.168.100.7:5000/session/<TOKEN>]
    ↓
Mobile scans QR
    ↓
/session/<token>
    ↓
    [Learning Paths: Camera & Files | Learn Permissions]
    ↓
Camera & Files (Click)
    ↓
/camera/<token>
    ↓
    [Permission Modal: Grant Access | Skip]
    ↓
    [Camera Feed | Capture | Uploaded Files | Upload]
```

---

## API Endpoints

- `GET /` - Main page with QR generator
- `GET /session/<token>` - Learning paths selector
- `GET /camera/<token>` - Camera + file storage
- `GET /permissions/<token>` - Permission education
- `POST /api/storage/upload/<token>` - Upload file
- `GET /api/storage/list/<token>` - List files
- `GET /api/storage/download/<token>/<filename>` - Download file
- `GET /api/permissions/tips` - Get security tips
- `GET /api/permissions/dangerous?platform=android|ios` - Get dangerous perms
- `GET /api/permissions/detail/<perm>?platform=android|ios` - Permission details

---

## Session Management

- **One QR per app start** – unique token generated at runtime
- **No persistence** – files cleared on app restart
- **Browser-based permissions** – uses standard `getUserMedia` API
- **Non-invasive learning** – user explicitly chooses files to upload

---

## For Teachers

1. Start the app: `run.bat` or `python backend/app.py`
2. Students see the QR on your screen (automatically generated)
3. They scan with their phone
4. They follow the learning path with real file & camera access
5. All activity is isolated to that session

