#!/bin/bash
# This script resizes an avatar image to 80x80 pixels for use in a navbar.
# Usage: ./resize_avatar_for_navbar.sh path_to_image

if [ -z "$1" ]; then
  echo "Usage: $0 path_to_image"
  exit 1
fi

magick "$1" -resize 80x80 avatar.png