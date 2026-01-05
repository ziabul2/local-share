# Local Network Sync - Implementation Guide

## Overview
The QR project now supports **secure local network device pairing** for file synchronization between phones and PCs on the same Wi-Fi network.

## Features

### 1. **Device Pairing**
- **QR Code Generation**: PC generates a unique pairing QR code with embedded device info
- **Token Authentication**: Each pairing uses a 24-byte secure token
- **Device IDs**: Unique identifiers for both PC and phone devices
- **Expiration**: Pairing tokens expire after 15 minutes for security

### 2. **TLS/HTTPS Support**
- **Self-Signed Certificates**: Automatically generated for local network security
- **Transparent HTTPS**: Server runs on `https://[LOCAL_IP]:5000` when TLS is available
- **Fallback**: Gracefully falls back to HTTP if certificate generation fails

### 3. **Photo Gallery Display**
- **All Photos Displayed**: Shows all uploaded photos and videos from:
  - User uploads via File Picker
  - Synced devices on local network
  - Server-side gallery storage
- **Lightbox Preview**: Click any photo to open full-screen lightbox
- **Video Support**: Video files marked with 🎬 badge, auto-detected by extension

### 4. **Local Network Sync**
- **Synced Device List**: Shows all paired devices and their sync status
- **File Metadata**: Tracks file counts, last sync time, and device names
- **Cross-Device Access**: Access files from all paired devices in one interface
- **Automatic Updates**: Gallery and device list refresh automatically (5-second intervals)

## Architecture

### Backend Components

#### `backend/pairing.py` - Device Pairing Manager
```python
PairingManager()
  ├── generate_pairing_qr_data() → Creates pairing data with device info
  ├── verify_pairing_token() → Validates tokens and checks expiration
  ├── confirm_pairing() → Confirms pairing from phone
  ├── get_paired_devices() → Lists all confirmed paired devices
  └── update_sync_info() → Updates device sync metadata
```

#### `backend/tls_setup.py` - Certificate Generation
- Uses `openssl` or Python `cryptography` library
- Generates 2048-bit RSA self-signed certificates
- Valid for 365 days
- Stored in `certs/` directory

#### `backend/app.py` - API Endpoints
```
POST   /api/pairing/generate      → Generate pairing QR
POST   /api/pairing/confirm       → Confirm pairing from phone
GET    /api/pairing/devices       → List paired devices
POST   /api/pairing/revoke/<token> → Revoke pairing
POST   /api/sync/<token>          → Sync files from device
```

### Frontend Components

#### `frontend/pairing.html` - PC Pairing Page
- Shows pairing QR code
- Displays local IP and device info
- Lists paired devices
- Allows QR regeneration and pairing revocation
- Mobile-friendly link to confirmation page

#### `frontend/pair-confirm.html` - Phone Confirmation Page
- Displays pairing token
- Device information (server IP, device name)
- Input field for phone device name
- Secure connection confirmation
- Redirects to explorer after successful pairing

#### `frontend/explorer.html` - Enhanced File Explorer
- **Synced Devices Panel**: Shows all paired devices and sync status
- **Photo Gallery**: Displays all photos and videos with lightbox preview
- **File Upload**: Upload files from Photo Picker or file input
- **Automatic Sync**: Polls synced devices every 5 seconds

## Flow Diagram

```
PC (Server)                           Phone (Client)
─────────────────────────────────────────────────────

1. User clicks "Start Device Pairing"
   ├─ Generate pairing token
   ├─ Create pairing QR (includes: IP, port, token, device_id)
   └─ Display on /pairing page

2. Phone scans QR code
   ├─ Parse pairing data
   ├─ Open /pair-confirm page
   └─ Display device info

3. User enters phone device name
   └─ Clicks "Confirm Pairing"
      ├─ Send to /api/pairing/confirm with:
      │  ├─ pairing_token
      │  ├─ phone_device_id
      │  └─ phone_device_name
      │
      └─ Server validates token
         ├─ Update pairing status → "confirmed"
         └─ Save pairing metadata

4. Phone redirected to /explorer/<token>
   ├─ Load gallery from /api/gallery/<token>
   ├─ Show local uploads + synced device files
   └─ Poll /api/pairing/devices every 5s

5. Photos automatically display
   ├─ Server-uploaded photos at /uploads/<token>/
   ├─ Device-synced photos from /api/sync
   └─ Lightbox preview on click
```

## Security Model

### Token-Based Authentication
- Each pairing uses a unique 24-byte token (base64-url encoded)
- Tokens are verified on all protected endpoints
- Tokens expire after 15 minutes if not confirmed
- Confirmed pairings stored for 30 days

### TLS/HTTPS
- Self-signed certificates for local network only
- No CA certificates needed (local Wi-Fi trusted)
- Prevents man-in-the-middle on open Wi-Fi
- HTTPS enforced by setting `protocol: https` in pairing data

### Local Network Only
- Device pairing QR code works only on the same Wi-Fi
- IP address embedded in QR ensures correct server connection
- Cross-device communication stays within LAN

## Usage

### For PC Users

1. **Start Pairing**:
   ```
   - Go to http://[PC_IP]:5000
   - Click "Start Device Pairing"
   - Share QR code with phone via screenshot/camera
   ```

2. **Manage Pairings**:
   ```
   - View /pairing to see all paired devices
   - Click "Revoke" to remove a device
   - Click "Regenerate QR" for a new pairing code
   ```

3. **View Synced Files**:
   ```
   - Go to /explorer to see gallery
   - Synced devices shown in green panel
   - All photos display with lightbox preview
   ```

### For Phone Users

1. **Scan & Confirm**:
   ```
   - Scan pairing QR with phone camera
   - Tap to open confirmation page
   - Enter phone device name
   - Click "Confirm Pairing"
   ```

2. **Access Files**:
   ```
   - Automatically redirected to /explorer
   - Select photos using Photo Picker
   - Photos appear in gallery and sync to PC
   ```

3. **Manage Pairings**:
   ```
   - Settings → Paired Devices (future feature)
   - Revoke pairing to disconnect device
   ```

## Pairing Data Format

```json
{
  "type": "device_pairing",
  "version": "1.0",
  "device_id": "a1b2c3d4",
  "device_name": "My PC",
  "ip": "192.168.1.100",
  "port": 5000,
  "pairing_token": "JaB2...base64url...token",
  "created_at": "2025-12-23T10:30:45.123456",
  "expires_at": "2025-12-23T10:45:45.123456",
  "protocol": "https"
}
```

## Persistent Storage

### `paired_devices.json`
```json
{
  "[pairing_token]": {
    "device_id": "phone_id",
    "device_name": "My iPhone",
    "ip": "192.168.1.50",
    "port": 5000,
    "paired_at": "2025-12-23T10:35:00",
    "confirmed_at": "2025-12-23T10:35:10",
    "expires_at": "2026-01-22T10:35:00",
    "status": "confirmed",
    "phone_device_id": "phone_device_123",
    "phone_device_name": "My iPhone",
    "synced_files": [
      {"name": "photo1.jpg", "size": 2456789, "type": "image"}
    ],
    "last_sync": "2025-12-23T10:40:00"
  }
}
```

### `certs/` Directory
```
certs/
├── cert.pem      (Self-signed certificate)
└── key.pem       (Private key)
```

## Configuration

### TLS Certificate Settings
- **Algorithm**: RSA 2048-bit
- **Validity**: 365 days
- **Format**: PEM
- **Common Name**: Local IP address

### Pairing Settings
- **Token Lifetime**: 15 minutes (pending), 30 days (confirmed)
- **Sync Poll Interval**: 5 seconds
- **Device Limit**: Unlimited (no hard limit enforced)

## Troubleshooting

### Certificate Issues
```
⚠ TLS setup failed: openssl not found
→ Solution: Install openssl or install cryptography package
  pip install cryptography
```

### QR Scan Fails
- Ensure phone is on same Wi-Fi as PC
- Check that firewall allows port 5000
- Verify local IP is correct (check with `ipconfig` on Windows)

### Photos Not Displaying
- Check `/uploads/<token>/` has files
- Verify file extensions are `.jpg`, `.png`, `.mp4`, etc.
- Check browser console for CORS or fetch errors

### Device Won't Pair
- QR expires after 15 minutes → regenerate
- Ensure phone can reach PC IP:port
- Try HTTP instead of HTTPS if TLS fails
- Check `paired_devices.json` for pairing status

## Future Enhancements

1. **Advanced Sync**:
   - Two-way sync (PC → Phone)
   - Selective folder sync
   - Sync scheduling

2. **Photo Organization**:
   - Auto-organize by date
   - Tag and collection support
   - Search and filter

3. **Sharing Features**:
   - Nearby Share integration
   - Cloud backup option
   - Shared albums

4. **Security**:
   - Device certificate pinning
   - End-to-end encryption
   - Two-factor pairing confirmation

## Testing Checklist

- [ ] QR generates with correct device info
- [ ] Phone scans QR and opens confirmation page
- [ ] Confirmation succeeds with valid token
- [ ] Paired devices appear in PC pairing page
- [ ] Photos upload and appear in gallery
- [ ] Lightbox opens on photo click
- [ ] Synced devices list updates automatically
- [ ] Photos display from both uploads and synced devices
- [ ] HTTPS works with self-signed cert
- [ ] Fallback to HTTP when TLS unavailable
- [ ] Pairing revocation works
- [ ] Device removal clears synced files list
