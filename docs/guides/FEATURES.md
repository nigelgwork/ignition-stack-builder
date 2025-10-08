# New Features Added

## 1. Dynamic Version Updates from Docker Hub

### What Changed
- Version lists are now fetched **automatically** from Docker Hub API in real-time
- No more manual updates needed to the catalog.json file

### How It Works
- Backend endpoint: `GET /versions/{app_id}`
- Fetches available tags from Docker Hub repositories
- Filters and sorts versions (newest first)
- Falls back to catalog versions if API fails

### Supported Apps
- **Ignition**: Automatically fetches all 8.x versions from `inductiveautomation/ignition`
- **PostgreSQL**: Automatically fetches versions from `postgres`
- **Other apps**: Will attempt to fetch from their respective Docker Hub repositories

### Example
```bash
curl http://localhost:8000/versions/ignition
```

Returns:
```json
{
  "versions": [
    "latest",
    "8.3.0",
    "8.1.50",
    "8.1.49",
    "8.1.48",
    ...
  ]
}
```

---

## 2. Module Selection System

### What Changed
- Replaced text input for modules with **checkbox-based multiselect**
- Visual grid layout showing all available Ignition modules
- Default modules pre-selected

### Available Modules
Built-in Ignition modules you can enable/disable:
- ✅ **perspective** (default)
- ✅ **vision** (default)
- ✅ **tag-historian** (default)
- ✅ **sql-bridge** (default)
- ✅ **alarm-notification** (default)
- ✅ **opc-ua** (default)
- ✅ **reporting** (default)
- sfc
- symbol-factory
- enterprise-administration
- sms-notification
- voice-notification

### How It Works
- Checkboxes in responsive grid layout
- Hover effects for better UX
- Selected modules converted to comma-separated `GATEWAY_MODULES_ENABLED` environment variable

---

## 3. 3rd Party Module Upload

### What Changed
- Replaced URL textarea with **file upload interface**
- Upload actual `.modl` files instead of entering URLs
- Files are included in the downloaded stack ZIP

### Features
- **File Upload**: Browse and select `.modl` files
- **Multiple Files**: Upload multiple 3rd party modules at once
- **File Management**: View uploaded files with size, remove individual files
- **Validation**: Only `.modl` files accepted

### How It Works
1. Click file input to browse for `.modl` files
2. Files are uploaded to backend endpoint: `POST /upload-module`
3. Files are base64 encoded and stored in instance config
4. When you download the stack, module files are included in `modules/{instance_name}/` directory
5. Each file shows filename and size with remove (✕) button

### File Storage
Downloaded stacks now include:
```
iiot-stack.zip
├── docker-compose.yml
├── .env
├── README.md
├── configs/
├── scripts/
└── modules/
    └── ignition-1/
        ├── custom-module-1.modl
        └── custom-module-2.modl
```

---

## 4. Updated Ignition Versions

### What Changed
- Added Ignition **8.3.x** versions (8.3.0, 8.3.1, 8.3.2)
- Updated 8.1.x versions to include latest releases
- Now **automatically pulls** from Docker Hub, so always up-to-date

---

## Technical Implementation

### Backend Changes

1. **New File**: `backend/docker_hub.py`
   - Docker Hub API integration
   - Version fetching and filtering
   - Caching with `@lru_cache`

2. **New Endpoint**: `GET /versions/{app_id}`
   - Dynamic version retrieval
   - Fallback to catalog if API fails

3. **New Endpoint**: `POST /upload-module`
   - Accepts `.modl` file uploads
   - Returns base64 encoded content
   - Validates file type

4. **Updated**: Module handling in docker-compose generation
   - Converts module arrays to comma-separated strings
   - Handles uploaded module files in ZIP download

5. **New Dependency**: `requests==2.31.0`
   - Required for Docker Hub API calls

### Frontend Changes

1. **New Component**: Multiselect with checkboxes
   - Grid layout of module options
   - Checkbox state management
   - Hover effects

2. **New Component**: File upload interface
   - File input with `.modl` filter
   - Uploaded files list
   - Remove file functionality

3. **New Functions**:
   - `handleFileUpload()`: Uploads files to backend
   - `removeUploadedModule()`: Removes uploaded files

4. **New CSS**:
   - `.multiselect-container`: Grid layout for checkboxes
   - `.file-upload-container`: File upload styling
   - `.uploaded-file-item`: Individual file display

---

## Usage Guide

### Selecting Ignition Modules

1. Add an Ignition instance
2. Scroll to "Modules" section
3. Check/uncheck modules you want
4. Default modules are pre-selected

### Uploading 3rd Party Modules

1. Add an Ignition instance
2. Scroll to "3rd Party Module URLs" section
3. Click the file input to browse
4. Select one or more `.modl` files
5. Files appear in the list below with size
6. Click ✕ to remove unwanted files
7. When you download the stack, modules are included

### Version Selection

All applications now show the most current versions available from Docker Hub. The list updates automatically when you reload the page.

---

## Benefits

✅ **Always Current**: Versions update automatically from Docker Hub
✅ **Better UX**: Visual checkboxes instead of text lists
✅ **Actual Files**: Upload real module files, not just URLs
✅ **Complete Stacks**: Downloaded ZIPs include all necessary files
✅ **Validation**: Only valid `.modl` files accepted
✅ **Flexibility**: Mix built-in and 3rd party modules easily

---

## API Reference

### Get Versions
```
GET /versions/{app_id}
```

Response:
```json
{
  "versions": ["latest", "8.3.0", "8.1.50", ...]
}
```

### Upload Module
```
POST /upload-module
Content-Type: multipart/form-data

file: <.modl file>
```

Response:
```json
{
  "filename": "custom-module.modl",
  "size": 1234567,
  "encoded": "base64_encoded_content..."
}
```

---

## Future Enhancements

Potential improvements for later:
- [ ] Auto-fetch versions on page load (optional toggle)
- [ ] Module dependency checking
- [ ] Module description tooltips
- [ ] Drag-and-drop file upload
- [ ] Bulk module upload
- [ ] Module version management
- [ ] Preview module details before upload
