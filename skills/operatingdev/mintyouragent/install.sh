#!/bin/bash
# MintYourAgent - Single Install Script
# Downloads everything and sets up the skill in one command

set -e

INSTALL_DIR="${1:-./mintyouragent}"
# Public repo URL (issue #7 - no private repo URLs)
REPO_URL="https://raw.githubusercontent.com/clawdhub/mintyouragent/main"

echo "🚀 Installing MintYourAgent to $INSTALL_DIR"
echo ""

# Verify SSL/network before starting (issue #8)
if ! curl -sS --max-time 10 "https://clawdhub.com" > /dev/null 2>&1; then
    echo "⚠️  Warning: Could not reach clawdhub.com"
    echo "   Continuing anyway..."
fi

# Create directory
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Download files with error checking
echo "📥 Downloading files..."

download_file() {
    local url="$1"
    local output="$2"
    if curl -sSL --fail "$url" -o "$output" 2>/dev/null; then
        echo "   ✓ $output"
    else
        echo "   ❌ Failed to download $output"
        echo "      URL: $url"
        return 1
    fi
}

download_file "$REPO_URL/mya.py" "mya.py" || exit 1
download_file "$REPO_URL/SKILL.md" "SKILL.md" || exit 1
chmod +x mya.py

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "📦 Python $PYTHON_VERSION detected"

# Install dependencies
echo "📦 Installing Python dependencies..."
if pip install solders requests 2>/dev/null; then
    echo "✅ Dependencies installed"
elif pip install --user solders requests 2>/dev/null; then
    echo "✅ Dependencies installed (user)"
elif pip3 install solders requests 2>/dev/null; then
    echo "✅ Dependencies installed (pip3)"
else
    echo "⚠️  Could not install dependencies automatically"
    echo "   Run manually: pip install solders requests"
    echo "   Or use a virtual environment:"
    echo "   python3 -m venv venv && source venv/bin/activate && pip install solders requests"
fi

echo ""
echo "✅ MintYourAgent installed!"
echo ""
echo "Data directory: ~/.mintyouragent/ (wallet, keys, config)"
echo ""
echo "Next steps:"
echo "  cd $INSTALL_DIR"
echo "  python mya.py setup       # Create wallet"
echo "  python mya.py wallet fund # Fund wallet"
echo "  python mya.py launch --help"
