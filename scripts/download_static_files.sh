#!/bin/bash
# Script to download Bootstrap and Bootstrap Icons for offline use
# Run this script on a machine with internet access, then copy the static folder to your server

echo "Downloading Bootstrap 5.3.0 and Bootstrap Icons 1.11.0..."
echo "==========================================================="

# Create directory structure
mkdir -p static/vendor/bootstrap/css
mkdir -p static/vendor/bootstrap/js
mkdir -p static/vendor/bootstrap-icons/fonts
mkdir -p static/vendor/bootstrap-icons/css

# Download Bootstrap CSS
echo "Downloading Bootstrap CSS..."
curl -L -o static/vendor/bootstrap/css/bootstrap.min.css \
  https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css

# Download Bootstrap JS Bundle
echo "Downloading Bootstrap JS Bundle..."
curl -L -o static/vendor/bootstrap/js/bootstrap.bundle.min.js \
  https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js

# Download Bootstrap Icons CSS
echo "Downloading Bootstrap Icons CSS..."
curl -L -o static/vendor/bootstrap-icons/css/bootstrap-icons.min.css \
  https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.min.css

# Download Bootstrap Icons Fonts
echo "Downloading Bootstrap Icons Fonts..."
curl -L -o static/vendor/bootstrap-icons/fonts/bootstrap-icons.woff \
  https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/fonts/bootstrap-icons.woff

curl -L -o static/vendor/bootstrap-icons/fonts/bootstrap-icons.woff2 \
  https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/fonts/bootstrap-icons.woff2

echo ""
echo "Download complete!"
echo "==========================================================="
echo "Files downloaded to: $(pwd)/static/vendor/"
echo ""
echo "NEXT STEPS:"
echo "1. Copy the entire 'static' folder to your offline server"
echo "2. Make sure Django's STATIC_ROOT is configured properly"
echo "3. Run: python manage.py collectstatic"
echo "4. Restart your Django application"
echo ""
echo "File sizes:"
ls -lh static/vendor/bootstrap/css/
ls -lh static/vendor/bootstrap/js/
ls -lh static/vendor/bootstrap-icons/css/
ls -lh static/vendor/bootstrap-icons/fonts/
