# Quick Start - Local Network Device Pairing

## Install Dependencies

```bash
pip install -r requirements.txt
```

This installs the cryptography library needed for TLS certificate generation.

## Run the Server

```bash
python backend/app.py
```

**Expected Output**:
```
✓ HTTPS enabled for local network access at https://192.168.1.100:5000

QR Pairing endpoint available at:
  - http://192.168.1.100:5000/pairing
  - https://192.168.1.100:5000/pairing (if TLS available)

Session URL: http://192.168.1.100:5000/session/[TOKEN]
```

## PC Setup (First Time)

1. Open http://[YOUR_LOCAL_IP]:5000 in a browser
2. Click **"🔒 Start Device Pairing"**
3. A pairing QR code will be generated
4. Share the QR code with your phone

## Phone Setup

1. **Option A - Scan QR with camera**:
   - Open device camera
   - Point at the PC screen QR code
   - Tap the notification to open pairing page

2. **Option B - Visit pairing URL directly**:
   - Type `http://[PC_IP]:5000/pairing` in phone browser
   - Click "Pair with PC"

3. **Confirm Pairing**:
   - Enter your phone's device name (e.g., "My iPhone")
   - Tap **"✓ Confirm Pairing"**
   - You'll be redirected to File Explorer

## Using File Explorer

### On PC
- Go to http://[PC_IP]:5000/explorer
- See "Local Network Sync" panel with paired devices
- Gallery shows all synced photos and uploads

### On Phone
- Auto-redirected after pairing
- Tap "Allow Access" to use Photo Picker
- Select photos from gallery
- Photos upload and appear immediately in gallery
- Can also browse Quick Access folders

## View Synced Photos

Both PC and Phone can:
1. Click any photo in the gallery to open full-screen lightbox
2. See file info (name, size, type, location)
3. Download files if needed

## Manage Pairings

### View Paired Devices
- Go to http://[PC_IP]:5000/pairing
- See all connected devices in the "Paired Devices" section
- Last sync time and file count shown

### Revoke a Device
- Click **"Revoke"** button next to device name
- Device loses access to shared files
- Must rescan QR to re-pair

### Regenerate QR
- Click **"🔄 Regenerate QR"**
- New pairing token generated
- Old tokens remain valid for 30 days

## Security Notes

✅ **Safe to use on public Wi-Fi** - Only devices that scan the QR code can pair

🔒 **HTTPS Enabled** - Self-signed certificate automatically generated

⏰ **Auto-Expiring** - Pending pairing tokens expire in 15 minutes

🔐 **Token-Based** - Each device gets unique authentication token

## Troubleshooting

### Can't reach server from phone
- Check phone is on **same Wi-Fi as PC**
- Try IP address instead of `localhost`
- Disable VPN on phone
- Check Windows Firewall allows port 5000

### QR code won't scan
- Increase brightness on PC screen
- Try scanning from 6 inches away
- Ensure room has good lighting
- Regenerate QR code

### Photos not uploading
- Check storage permissions on phone
- Ensure network connection is stable
- Check browser console for errors (F12)
- Try refreshing the page

### HTTPS errors
- This is normal for self-signed certificates on local network
- Click "Continue" or "Ignore warning" in your browser
- Certificates are only for your local network (not shared)

## Next Steps

1. **Upload Photos**: Use "Allow Access" → Photo Picker to select photos
2. **Organize Files**: Browse Quick Access folders (DCIM, Pictures, Videos, etc.)
3. **Share Files**: Click photos to view details and download
4. **Multi-Device**: Pair multiple phones with the same PC
5. **Auto-Sync**: Files automatically sync between devices on same Wi-Fi

## Advanced Features

### Sync Multiple Devices
- Pair as many phones/tablets as you want
- All devices see each other's files
- PC acts as central hub for file synchronization

### Cross-Device File Access
- Each device can browse files from other paired devices
- See sync status and last-synced time
- Download files from other devices through explorer

### Persistent Pairing
- Pairings stored in `paired_devices.json`
- Devices remain paired between server restarts
- Confirmed pairings last 30 days

## File Storage

- **Uploads**: `uploads/[session_token]/[filename]`
- **Pairings**: `paired_devices.json`
- **Certificates**: `certs/cert.pem`, `certs/key.pem`

All relative to project root.

## More Information

See [LOCAL_NETWORK_SYNC.md](LOCAL_NETWORK_SYNC.md) for complete documentation.
