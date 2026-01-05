# API Reference - Local Network Sync

Complete API documentation for the QR device pairing system.

## Base URL

```
http://[LOCAL_IP]:5000
https://[LOCAL_IP]:5000  (if TLS available)
```

## Pairing Endpoints

### Generate Pairing QR
```
POST /api/pairing/generate
Content-Type: application/json

Body:
{
  "device_name": "My PC"  // optional
}

Response:
{
  "qr_data_url": "data:image/png;base64,...",
  "pairing_token": "JaB2...secure_token",
  "device_id": "a1b2c3d4",
  "pairing_data": {
    "type": "device_pairing",
    "version": "1.0",
    "device_id": "a1b2c3d4",
    "device_name": "My PC",
    "ip": "192.168.1.100",
    "port": 5000,
    "pairing_token": "JaB2...secure_token",
    "created_at": "2025-12-23T10:30:45",
    "expires_at": "2025-12-23T10:45:45",
    "protocol": "https"
  }
}
```

### Confirm Pairing
```
POST /api/pairing/confirm
Content-Type: application/json

Body:
{
  "pairing_token": "JaB2...secure_token",
  "phone_device_id": "phone_device_123",
  "phone_device_name": "My iPhone"
}

Response:
{
  "ok": true,
  "message": "Device 'My iPhone' paired successfully",
  "pairing_token": "JaB2...secure_token"
}

Error:
{
  "error": "invalid or expired pairing token"
}  → Status 401
```

### List Paired Devices
```
GET /api/pairing/devices

Response:
{
  "devices": [
    {
      "device_id": "phone_device_123",
      "device_name": "My iPhone",
      "status": "confirmed",
      "paired_at": "2025-12-23T10:35:00",
      "confirmed_at": "2025-12-23T10:35:10",
      "expires_at": "2026-01-22T10:35:00",
      "phone_device_id": "phone_device_123",
      "phone_device_name": "My iPhone",
      "synced_files": [
        {
          "name": "photo1.jpg",
          "size": 2456789,
          "type": "image"
        }
      ],
      "last_sync": "2025-12-23T10:40:00"
    }
  ]
}
```

### Revoke Pairing
```
POST /api/pairing/revoke/<pairing_token>

Response:
{
  "ok": true,
  "message": "Pairing revoked"
}

Error:
{
  "error": "Pairing not found"
}  → Status 404
```

## Gallery Endpoints

### Get Gallery Files
```
GET /api/gallery/<session_token>

Response:
{
  "gallery": [
    {
      "name": "photo1.jpg",
      "type": "image",
      "path": "/uploads/<token>/photo1.jpg",
      "size": 2456789
    },
    {
      "name": "video1.mp4",
      "type": "video",
      "path": "/uploads/<token>/video1.mp4",
      "size": 47364829
    }
  ]
}
```

## Storage/Upload Endpoints

### Upload File
```
POST /api/storage/upload/<session_token>
Content-Type: multipart/form-data

Form Data:
- file: [File object]

Response:
{
  "ok": true,
  "filename": "photo1.jpg"
}

Error:
{
  "error": "no file part"
}  → Status 400
```

### Download File
```
GET /api/storage/download/<session_token>/<filename>

Response:
[File binary data]

Error:
404 Not Found
```

## Sync Endpoint

### Sync Files from Device
```
POST /api/sync/<pairing_token>
Content-Type: application/json

Body:
{
  "files": [
    {
      "name": "photo1.jpg",
      "size": 2456789,
      "type": "image"
    }
  ]
}

Response:
{
  "ok": true,
  "synced": 1,
  "message": "Synced 1 files from paired device"
}

Error:
{
  "error": "invalid pairing token"
}  → Status 401
```

## Admin Endpoints

### Get All Sessions
```
GET /api/admin/sessions

Response:
{
  "sessions": [
    {
      "token": "[SESSION_TOKEN]",
      "granted": true,
      "created_at": "2025-12-23T10:30:45",
      "files": [
        {
          "name": "photo1.jpg",
          "size": 2456789
        }
      ],
      "file_count": 1
    }
  ]
}
```

### Grant Permission
```
POST /api/session/grant/<session_token>

Response:
{
  "ok": true
}
```

## Page Endpoints

### Landing Page
```
GET /
→ Redirects to index.html with session QR
```

### Device Pairing Page
```
GET /pairing
→ Returns pairing.html
```

### Phone Confirmation Page
```
GET /pair-confirm
→ Returns pair-confirm.html
```

### File Explorer
```
GET /explorer/<session_token>
→ Returns explorer.html with token
```

### Admin Panel
```
GET /admin
→ Returns admin.html
```

### Session Page (Learning)
```
GET /session/<session_token>
→ Returns session.html with token
```

## Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad request (missing data) |
| 401 | Unauthorized (invalid token) |
| 404 | Not found (resource doesn't exist) |
| 500 | Server error |

## Error Response Format

```json
{
  "error": "Description of the error"
}
```

## Token Format

All tokens are:
- Base64-URL encoded
- 16-24 bytes of random data
- Safe for use in URLs and JSON
- Treated as case-sensitive

Example: `JaB2xY9_-w9dKmN8pL3qR5tS7u1vW0x`

## Rate Limiting

Currently no rate limiting. For production, consider adding:
- Per-token rate limits (e.g., 100 req/min)
- Per-IP rate limits (e.g., 500 req/min)
- Pairing endpoint limits (e.g., 10 new pairings/hour)

## CORS

All endpoints include `@app.after_request` CORS headers:
- `Access-Control-Allow-Origin: *`
- `Access-Control-Allow-Methods: GET, POST, OPTIONS`
- `Access-Control-Allow-Headers: Content-Type`

## Authentication

### Token Validation
All endpoints (except /api/pairing/generate) that use tokens:
1. Extract token from request
2. Look up in `PAIRED_DEVICES` dict or `SESSIONS` dict
3. Verify token exists and hasn't expired
4. Allow/deny based on validation

### Token Expiration
- Pending tokens: 15 minutes
- Confirmed pairings: 30 days
- Automatic cleanup on validation failure

## Payload Limits

- Max file size: No hard limit (configurable)
- Max filename length: 255 characters
- Max pairing devices: No limit
- Max files per session: No limit

## Content Types

### Request
- `application/json` - For JSON payloads
- `multipart/form-data` - For file uploads

### Response
- `application/json` - All API responses
- `image/png` - QR code data URL (embedded)
- `[various]` - File downloads

## Caching

Current implementation:
- No caching headers (each request is fresh)
- Gallery is re-scanned on each `/api/gallery/` request
- Device list is re-read from JSON on each `/api/pairing/devices` request

For production, consider adding:
- Cache-Control headers
- ETag support
- Last-Modified timestamps

## Webhooks (Future)

Planned webhooks for:
- Device paired
- File uploaded
- Sync completed
- Device disconnected

## Versioning

Current API version: 1.0 (in pairing_data.version)

Future versions should:
- Include `api/v1/`, `api/v2/`, etc. in paths
- Support multiple versions simultaneously
- Provide migration guide for breaking changes

## Example Usage

### JavaScript/Fetch

```javascript
// Generate pairing QR
const response = await fetch('/api/pairing/generate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ device_name: 'My PC' })
});
const data = await response.json();

// Confirm pairing
const confirmResponse = await fetch('/api/pairing/confirm', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    pairing_token: data.pairing_token,
    phone_device_id: 'phone_123',
    phone_device_name: 'My iPhone'
  })
});

// Upload file
const formData = new FormData();
formData.append('file', fileObject);
const uploadResponse = await fetch(`/api/storage/upload/${token}`, {
  method: 'POST',
  body: formData
});

// Get gallery
const galleryResponse = await fetch(`/api/gallery/${token}`);
const gallery = await galleryResponse.json();
```

### cURL

```bash
# Generate pairing QR
curl -X POST http://localhost:5000/api/pairing/generate \
  -H "Content-Type: application/json" \
  -d '{"device_name":"My PC"}'

# Confirm pairing
curl -X POST http://localhost:5000/api/pairing/confirm \
  -H "Content-Type: application/json" \
  -d '{
    "pairing_token":"JaB2...",
    "phone_device_id":"phone_123",
    "phone_device_name":"My iPhone"
  }'

# Get paired devices
curl http://localhost:5000/api/pairing/devices

# Get gallery
curl http://localhost:5000/api/gallery/[TOKEN]
```

### Python Requests

```python
import requests

# Generate pairing QR
response = requests.post(
    'http://localhost:5000/api/pairing/generate',
    json={'device_name': 'My PC'}
)
data = response.json()

# Confirm pairing
confirm = requests.post(
    'http://localhost:5000/api/pairing/confirm',
    json={
        'pairing_token': data['pairing_token'],
        'phone_device_id': 'phone_123',
        'phone_device_name': 'My iPhone'
    }
)

# Upload file
with open('photo.jpg', 'rb') as f:
    upload = requests.post(
        f'http://localhost:5000/api/storage/upload/{token}',
        files={'file': f}
    )

# Get gallery
gallery = requests.get(
    f'http://localhost:5000/api/gallery/{token}'
).json()
```

## Debugging

### Enable Debug Mode
```python
# In backend/app.py
app.run(debug=True, host='0.0.0.0', port=5000)
```

### Check Browser Console
- F12 → Console tab
- Look for fetch errors
- Check network tab for requests

### Check Server Logs
- Terminal running Flask shows all requests
- Look for error messages
- Check status codes

### Test Endpoints with Postman
1. Download Postman
2. Import API collection (future)
3. Test each endpoint
4. View responses and headers

## Migration Guide

### v1.0 to Future Versions
- API versioning: Use `/api/v2/` prefixes
- Backward compatibility: Keep v1 endpoints
- Documentation: Update version in responses
- Deprecation: Give 6-month notice

---

**For more information, see:**
- [LOCAL_NETWORK_SYNC.md](LOCAL_NETWORK_SYNC.md) - Architecture
- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Technical details
- [QUICK_START.md](QUICK_START.md) - Usage examples
