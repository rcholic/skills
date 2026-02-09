#!/bin/bash
# ⚠️ DEPRECATED - Use Python version instead:
#    pip install solders requests
#    python mya.py setup
#
# This bash version requires solana-cli and may have PATH issues.
# The Python version works everywhere with no extra dependencies.

echo "⚠️  This script is deprecated. Use the Python version:"
echo "   pip install solders requests"
echo "   python mya.py setup"
echo ""
echo "Continuing with bash version in 3 seconds... (Ctrl+C to cancel)"
sleep 3

set -e  # Exit on error

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WALLET_FILE="$SKILL_DIR/wallet.json"

# Check if wallet already exists
if [ -f "$WALLET_FILE" ]; then
    echo "⚠️  Wallet already exists at: $WALLET_FILE"
    echo "To view address: ./wallet.sh address"
    echo "To regenerate, delete wallet.json first (you'll lose access to that wallet!)"
    exit 0
fi

# Function to install Solana CLI
install_solana() {
    echo "📦 Installing Solana CLI tools..."
    
    # Download and run installer
    if ! sh -c "$(curl -sSfL https://release.anza.xyz/stable/install)"; then
        echo "❌ Failed to install Solana CLI"
        echo "Try manual install: https://docs.solanalabs.com/cli/install"
        exit 1
    fi
    
    # Add to PATH for this session
    export PATH="$HOME/.local/share/solana/install/active_release/bin:$PATH"
    
    # Try to add to shell profile
    SHELL_PROFILE=""
    if [ -f "$HOME/.bashrc" ]; then
        SHELL_PROFILE="$HOME/.bashrc"
    elif [ -f "$HOME/.zshrc" ]; then
        SHELL_PROFILE="$HOME/.zshrc"
    elif [ -f "$HOME/.profile" ]; then
        SHELL_PROFILE="$HOME/.profile"
    fi
    
    if [ -n "$SHELL_PROFILE" ]; then
        if ! grep -q "solana/install/active_release/bin" "$SHELL_PROFILE" 2>/dev/null; then
            echo 'export PATH="$HOME/.local/share/solana/install/active_release/bin:$PATH"' >> "$SHELL_PROFILE"
            echo "✅ Added Solana to $SHELL_PROFILE"
        fi
    fi
}

# Check for solana-keygen
if ! command -v solana-keygen &> /dev/null; then
    # Check if it's installed but not in PATH
    if [ -f "$HOME/.local/share/solana/install/active_release/bin/solana-keygen" ]; then
        export PATH="$HOME/.local/share/solana/install/active_release/bin:$PATH"
    else
        install_solana
    fi
fi

# Verify installation
if ! command -v solana-keygen &> /dev/null; then
    echo "❌ solana-keygen not found after installation"
    echo "Please restart your terminal and run setup.sh again"
    exit 1
fi

# Generate new keypair
echo "🔑 Generating new Solana wallet..."
if ! solana-keygen new --outfile "$WALLET_FILE" --no-bip39-passphrase --force; then
    echo "❌ Failed to generate keypair"
    exit 1
fi

# Get the address
ADDRESS=$(solana-keygen pubkey "$WALLET_FILE")

echo ""
echo "✅ Wallet created!"
echo "📍 Address: $ADDRESS"
echo "📁 Keypair: $WALLET_FILE"
echo ""
echo "⚠️  IMPORTANT: Back up wallet.json - it contains your private key!"
echo "💰 Fund this wallet with SOL before launching tokens."
echo ""
echo "Next steps:"
echo "  ./wallet.sh balance    # Check balance"
echo "  ./wallet.sh export     # Export private key for Phantom"
echo "  ./launch.sh --help     # Launch a token"
