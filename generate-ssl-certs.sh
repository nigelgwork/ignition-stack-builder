#!/bin/bash

# Generate self-signed SSL certificates for local development
# These certificates will be used by nginx for HTTPS

CERT_DIR="./frontend/ssl"
DAYS_VALID=365

echo "🔐 Generating self-signed SSL certificates..."

# Create SSL directory if it doesn't exist
mkdir -p "$CERT_DIR"

# Generate private key and certificate
openssl req -x509 -nodes -days $DAYS_VALID -newkey rsa:2048 \
  -keyout "$CERT_DIR/nginx-selfsigned.key" \
  -out "$CERT_DIR/nginx-selfsigned.crt" \
  -subj "/C=AU/ST=SA/L=Adelaide/O=Ignition Stack Builder/OU=Development/CN=localhost" \
  -addext "subjectAltName=DNS:localhost,DNS:*.localhost,IP:127.0.0.1"

# Generate Diffie-Hellman parameters for added security
echo "🔐 Generating Diffie-Hellman parameters (this may take a minute)..."
openssl dhparam -out "$CERT_DIR/dhparam.pem" 2048

# Set appropriate permissions
chmod 600 "$CERT_DIR/nginx-selfsigned.key"
chmod 644 "$CERT_DIR/nginx-selfsigned.crt"
chmod 644 "$CERT_DIR/dhparam.pem"

echo "✅ SSL certificates generated successfully!"
echo "📁 Certificates location: $CERT_DIR/"
echo ""
echo "⚠️  Note: These are self-signed certificates for development only."
echo "    Your browser will show a security warning - this is normal."
echo "    Click 'Advanced' and 'Proceed to localhost' to continue."
echo ""
echo "🔄 Next steps:"
echo "   1. Restart the frontend container: docker-compose restart frontend"
echo "   2. Access the app via HTTPS: https://localhost:3500"
