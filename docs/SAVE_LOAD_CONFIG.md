# Save & Load Configuration Feature

## Overview

The IIoT Stack Builder now supports saving and loading stack configurations as encrypted files. This allows you to:
- Save complex configurations for reuse
- Share configurations securely with team members
- Create templates for common stack setups
- Back up your configuration before making changes

## Security

**Encryption Method**: AES-256-GCM with PBKDF2 key derivation
- Industry-standard encryption
- Password-based encryption (client-side only)
- Your password never leaves your browser
- 100,000 PBKDF2 iterations for key strengthening

**File Format**: `.iiotstack` (encrypted binary format)

## How to Use

### Saving a Configuration

1. Configure your stack with the desired services and settings
2. Click the **💾 Save Config** button
3. Enter a password (minimum 8 characters)
4. Click **Save**
5. Your configuration will be downloaded as `stack-config-YYYY-MM-DD.iiotstack`

**What's Saved:**
- All selected services and their configurations
- Global settings (timezone, restart policy, ntfy monitoring)
- Integration settings (reverse proxy, MQTT, OAuth, database, email)
- Service instances and their custom configs

**Not Saved:**
- Generated previews or downloaded stacks
- Temporary UI state
- Backend processing data

### Loading a Configuration

1. Click the **📂 Load Config** button
2. Select your `.iiotstack` file
3. Enter the password you used when saving
4. Click **Load**
5. Your configuration will be restored

**What Happens:**
- All current services are replaced with loaded configuration
- Global and integration settings are restored
- Configuration is validated before applying
- Invalid configurations are rejected with error message

## Password Requirements

- **Minimum length**: 8 characters
- **Recommended**: Use a strong, unique password
- **Storage**: Password is NOT saved anywhere - you must remember it
- **Recovery**: If you forget the password, the file cannot be decrypted

## Security Best Practices

### ✅ Do:
- Use strong, unique passwords (12+ characters recommended)
- Store passwords in a secure password manager
- Keep encrypted files in secure locations
- Share files through secure channels (encrypted email, secure file sharing)

### ❌ Don't:
- Use weak passwords like "password123"
- Share passwords and files together in the same message
- Store passwords in plain text files
- Email files without additional encryption

## File Sharing

When sharing configurations with team members:

1. **Share the file separately from the password**
   - Send file via one channel (e.g., email)
   - Send password via different channel (e.g., Slack DM, phone)

2. **Use secure file sharing**
   - Encrypted file sharing services
   - Company secure file storage
   - VPN-protected network shares

3. **Consider time-limited passwords**
   - Share password verbally when possible
   - Change password periodically for frequently-shared configs

## Common Use Cases

### Template Creation
Save common stack configurations as templates:
- `dev-stack-template.iiotstack` - Development environment
- `prod-ignition-postgres.iiotstack` - Production Ignition + DB
- `monitoring-stack.iiotstack` - Grafana + Prometheus setup

### Backup Before Changes
1. Save current configuration
2. Make experimental changes
3. Load backup if changes don't work

### Team Collaboration
1. Team lead creates standard configuration
2. Encrypts and shares with team
3. Team members load and customize as needed

### Version Control
Save configurations with descriptive names:
- `stack-v1.0-2025-10-07.iiotstack`
- `stack-v1.1-added-mqtt-2025-10-08.iiotstack`
- `stack-v2.0-production-ready-2025-10-09.iiotstack`

## Troubleshooting

### "Invalid password or corrupted file"
- **Cause**: Wrong password or file is damaged
- **Solution**:
  - Verify you're using the correct password
  - Re-download the file if it may be corrupted
  - Try saving a new configuration to test the feature

### "Invalid configuration"
- **Cause**: Configuration references services no longer in catalog
- **Solution**:
  - Check if services were removed in updates
  - Manually remove invalid services and save new config
  - Contact support if issue persists

### "Password must be at least 8 characters"
- **Cause**: Password too short
- **Solution**: Use a longer password (12+ recommended)

### File won't load
- **Cause**: File extension or format issue
- **Solution**:
  - Ensure file has `.iiotstack` extension
  - Don't edit the file manually
  - Don't open file in text editors (it's encrypted binary)

## Technical Details

### Encryption Specification
- **Algorithm**: AES-256-GCM
- **Key Derivation**: PBKDF2-SHA256
- **Iterations**: 100,000
- **Salt**: 16 bytes (random per file)
- **IV**: 12 bytes (random per encryption)
- **Key Length**: 256 bits

### File Structure
```
[16 bytes: salt][12 bytes: IV][remaining: encrypted data]
```

### API Endpoints

**Validate Configuration**:
```
POST /validate-config
Content-Type: application/json

{
  "instances": [...],
  "global_settings": {...},
  "integration_settings": {...}
}
```

**Response**:
```json
{
  "valid": true,
  "config": {...},
  "message": "Configuration is valid"
}
```

### Client-Side Code

Encryption/decryption is performed entirely in the browser using Web Crypto API:
- No server-side encryption/decryption
- Password never sent to server
- Server only validates configuration structure

## Feature Limitations

### Current Limitations
- Password cannot be recovered if forgotten
- File is not human-readable (encrypted)
- Requires modern browser with Web Crypto API support
- Configuration must be valid for current catalog version

### Future Enhancements (Potential)
- Password hints (stored separately)
- Multiple password support
- Configuration versioning and migration
- Cloud backup integration
- Team/organizational shared configs

## Browser Support

**Requires**: Web Crypto API support

**Supported Browsers**:
- ✅ Chrome 37+
- ✅ Firefox 34+
- ✅ Safari 11+
- ✅ Edge 79+
- ✅ Opera 24+

**Not Supported**:
- ❌ IE 11 and older
- ❌ Very old mobile browsers

## Privacy & Data

### What We Store
- **Nothing**: Passwords and configurations are never sent to our servers
- **Validation only**: When loading, only the configuration structure is validated server-side

### What You Store
- **Encrypted file**: On your local computer
- **Password**: In your memory or password manager

### Data Flow
1. **Saving**: Browser → Encrypt → Download to your computer
2. **Loading**: Your computer → Browser → Decrypt → Validate with server → Apply

The server never sees your password or unencrypted configuration.

## Support

If you encounter issues:
1. Check this documentation
2. Verify you're using a supported browser
3. Test with a simple configuration
4. Check browser console for error messages
5. Report issues on GitHub

## Examples

### Example: Save Development Template

```javascript
// 1. Configure stack in UI with:
//    - Ignition (standard edition)
//    - PostgreSQL (latest)
//    - Grafana (latest)
//    - MQTT broker (EMQX)
//
// 2. Click Save Config
// 3. Password: "devStack2025!"
// 4. File saved: stack-config-2025-10-07.iiotstack
```

### Example: Load and Customize

```javascript
// 1. Click Load Config
// 2. Select: stack-config-2025-10-07.iiotstack
// 3. Enter password: "devStack2025!"
// 4. Configuration loaded
// 5. Customize as needed (add/remove services)
// 6. Save as new config with different password
```

### Example: Team Distribution

```
Team Lead:
1. Create standard production configuration
2. Save with password: "TeamProdStack2025"
3. Share file via secure company drive
4. Share password via Slack DM to team members

Team Members:
1. Download file from company drive
2. Load with password from Slack
3. Customize for their specific needs
4. Deploy their customized stack
```

---

**Security Reminder**: Never share passwords and encrypted files in the same communication channel!
