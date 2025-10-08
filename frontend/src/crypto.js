/**
 * Client-side encryption/decryption utilities for stack configurations
 * Uses Web Crypto API with AES-256-GCM and PBKDF2 key derivation
 */

const SALT_LENGTH = 16; // bytes
const IV_LENGTH = 12; // bytes for GCM
const ITERATIONS = 100000; // PBKDF2 iterations
const KEY_LENGTH = 256; // bits

/**
 * Derive encryption key from password using PBKDF2
 */
async function deriveKey(password, salt) {
  const encoder = new TextEncoder();
  const passwordBuffer = encoder.encode(password);

  // Import password as key material
  const keyMaterial = await crypto.subtle.importKey(
    'raw',
    passwordBuffer,
    'PBKDF2',
    false,
    ['deriveKey']
  );

  // Derive AES key
  return crypto.subtle.deriveKey(
    {
      name: 'PBKDF2',
      salt: salt,
      iterations: ITERATIONS,
      hash: 'SHA-256'
    },
    keyMaterial,
    {
      name: 'AES-GCM',
      length: KEY_LENGTH
    },
    false,
    ['encrypt', 'decrypt']
  );
}

/**
 * Encrypt stack configuration
 * @param {Object} config - Stack configuration object
 * @param {string} password - User password
 * @returns {string} Base64-encoded encrypted data with salt and IV
 */
export async function encryptConfig(config, password) {
  if (!password || password.length < 8) {
    throw new Error('Password must be at least 8 characters');
  }

  // Generate random salt and IV
  const salt = crypto.getRandomValues(new Uint8Array(SALT_LENGTH));
  const iv = crypto.getRandomValues(new Uint8Array(IV_LENGTH));

  // Derive key
  const key = await deriveKey(password, salt);

  // Convert config to JSON string
  const encoder = new TextEncoder();
  const data = encoder.encode(JSON.stringify(config));

  // Encrypt
  const encrypted = await crypto.subtle.encrypt(
    {
      name: 'AES-GCM',
      iv: iv
    },
    key,
    data
  );

  // Combine salt + iv + encrypted data
  const combined = new Uint8Array(
    salt.length + iv.length + encrypted.byteLength
  );
  combined.set(salt, 0);
  combined.set(iv, salt.length);
  combined.set(new Uint8Array(encrypted), salt.length + iv.length);

  // Convert to base64
  return btoa(String.fromCharCode(...combined));
}

/**
 * Decrypt stack configuration
 * @param {string} encryptedData - Base64-encoded encrypted data
 * @param {string} password - User password
 * @returns {Object} Decrypted stack configuration object
 */
export async function decryptConfig(encryptedData, password) {
  if (!password) {
    throw new Error('Password is required');
  }

  try {
    // Decode base64
    const combined = new Uint8Array(
      atob(encryptedData)
        .split('')
        .map(char => char.charCodeAt(0))
    );

    // Extract salt, IV, and encrypted data
    const salt = combined.slice(0, SALT_LENGTH);
    const iv = combined.slice(SALT_LENGTH, SALT_LENGTH + IV_LENGTH);
    const encrypted = combined.slice(SALT_LENGTH + IV_LENGTH);

    // Derive key
    const key = await deriveKey(password, salt);

    // Decrypt
    const decrypted = await crypto.subtle.decrypt(
      {
        name: 'AES-GCM',
        iv: iv
      },
      key,
      encrypted
    );

    // Convert to string and parse JSON
    const decoder = new TextDecoder();
    const jsonString = decoder.decode(decrypted);
    return JSON.parse(jsonString);
  } catch (error) {
    if (error.name === 'OperationError') {
      throw new Error('Invalid password or corrupted file');
    }
    throw new Error(`Decryption failed: ${error.message}`);
  }
}

/**
 * Export encrypted config as downloadable file
 * @param {Object} config - Stack configuration object
 * @param {string} password - User password
 * @param {string} filename - Optional filename (default: stack-config.iiotstack)
 */
export async function downloadEncryptedConfig(config, password, filename = 'stack-config.iiotstack') {
  try {
    const encrypted = await encryptConfig(config, password);

    // Create blob and download
    const blob = new Blob([encrypted], { type: 'application/octet-stream' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    return true;
  } catch (error) {
    throw new Error(`Failed to export config: ${error.message}`);
  }
}

/**
 * Import and decrypt config from file
 * @param {File} file - Uploaded .iiotstack file
 * @param {string} password - User password
 * @returns {Object} Decrypted stack configuration object
 */
export async function importEncryptedConfig(file, password) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();

    reader.onload = async (e) => {
      try {
        const encryptedData = e.target.result;
        const config = await decryptConfig(encryptedData, password);
        resolve(config);
      } catch (error) {
        reject(error);
      }
    };

    reader.onerror = () => {
      reject(new Error('Failed to read file'));
    };

    reader.readAsText(file);
  });
}

/**
 * Validate config structure
 * @param {Object} config - Stack configuration object
 * @returns {boolean} True if valid
 */
export function validateConfigStructure(config) {
  if (!config || typeof config !== 'object') {
    throw new Error('Invalid config: must be an object');
  }

  if (!Array.isArray(config.instances)) {
    throw new Error('Invalid config: instances must be an array');
  }

  for (const instance of config.instances) {
    if (!instance.app_id || !instance.instance_name) {
      throw new Error('Invalid instance: missing app_id or instance_name');
    }
  }

  return true;
}
