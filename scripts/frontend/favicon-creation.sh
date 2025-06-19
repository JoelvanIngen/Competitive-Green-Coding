#!/bin/bash

# Next.js App Router Essential Favicon Generator
# This script generates only the essential favicons for Next.js App Router automatic handling
# Place your source image as 'favicon-source.png' in the project root and run this script

set -e  # Exit on any error

# Configuration
if [ -n "$1" ]; then
    SOURCE_FILE="$1"
else
    echo "No source file specified. Give the path to your source image as the first argument."
    echo "Usage: $0 <path_to_source_image>"
    exit 1
fi

APP_DIR="favicons"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if source file exists
if [ ! -f "$SOURCE_FILE" ]; then
    print_error "Source file '$SOURCE_FILE' not found!"
    echo "Please place your source image as 'favicon-source.png' in the project root."
    echo "Recommended source image size: at least 512x512 pixels"
    exit 1
fi

# Get source image dimensions for validation
SOURCE_INFO=$(identify "$SOURCE_FILE" 2>/dev/null || echo "")
if [ -z "$SOURCE_INFO" ]; then
    print_error "Unable to read source image. Please check if '$SOURCE_FILE' is a valid image file."
    exit 1
fi

SOURCE_WIDTH=$(echo "$SOURCE_INFO" | cut -d' ' -f3 | cut -d'x' -f1)
SOURCE_HEIGHT=$(echo "$SOURCE_INFO" | cut -d' ' -f3 | cut -d'x' -f2)

print_status "Source image: ${SOURCE_WIDTH}x${SOURCE_HEIGHT} pixels"

# Warn if source image is too small
if [ "$SOURCE_WIDTH" -lt 256 ] || [ "$SOURCE_HEIGHT" -lt 256 ]; then
    print_warning "Source image is smaller than 256x256. For best results, use a larger source image."
fi

# Create app directory if it doesn't exist
mkdir -p "$APP_DIR"

print_status "Generating essential favicons for Next.js App Router..."

# Generate favicon.ico (legacy support - 16x16, 32x32, 48x48)
print_status "Generating favicon.ico..."
magick "$SOURCE_FILE" \
    \( -clone 0 -resize 16x16 \) \
    \( -clone 0 -resize 32x32 \) \
    \( -clone 0 -resize 48x48 \) \
    -delete 0 "$APP_DIR/favicon.ico"

# Generate icon.png (modern browsers - 32x32)
print_status "Generating icon.png..."
magick "$SOURCE_FILE" -resize 32x32 "$APP_DIR/icon.png"

# Generate apple-icon.png (Apple devices - 180x180)
print_status "Generating apple-icon.png..."
magick "$SOURCE_FILE" -resize 180x180 "$APP_DIR/apple-icon.png"

print_success "Essential favicons generated successfully!"
echo ""
print_status "Generated files in '$APP_DIR' directory:"
echo "  ✓ favicon.ico (16x16, 32x32, 48x48 - legacy browsers)"
echo "  ✓ icon.png (32x32 - modern browsers)"
echo "  ✓ apple-icon.png (180x180 - Apple devices)"
echo ""
print_status "Put all files inside '$APP_DIR'in the /app directory. Next.js App Router will automatically:"
echo "  • Generate appropriate <link> tags"
echo "  • Serve favicons at the correct routes"
echo "  • Handle browser compatibility"
echo ""
print_success "Setup complete! Your Next.js app has clean, automatic favicon support."