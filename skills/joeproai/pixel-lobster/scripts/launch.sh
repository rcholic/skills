#!/bin/bash
# Launch Pixel Lobster
# Usage: bash launch.sh [--system|--tts]

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_DIR="$SCRIPT_DIR/../assets/app"

cd "$APP_DIR" || exit 1

# Install deps if needed
if [ ! -d "node_modules" ]; then
  echo "Installing dependencies..."
  npm install
fi

# Override audio mode if flag provided
if [ "$1" = "--system" ]; then
  echo "Starting in system audio mode..."
  npx electron . --audio-mode=system
elif [ "$1" = "--tts" ]; then
  echo "Starting in TTS mode..."
  npx electron . --audio-mode=tts
else
  echo "Starting pixel lobster..."
  npx electron .
fi
