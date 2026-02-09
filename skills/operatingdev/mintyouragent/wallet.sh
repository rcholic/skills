#!/bin/bash
# MintYourAgent Wallet Management

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WALLET_FILE="$SKILL_DIR/wallet.json"

# Use Helius RPC if available, fallback to public
RPC_URL="${HELIUS_RPC:-https://api.mainnet-beta.solana.com}"

# Ensure Solana CLI is in PATH
if [ -d "$HOME/.local/share/solana/install/active_release/bin" ]; then
    export PATH="$HOME/.local/share/solana/install/active_release/bin:$PATH"
fi

# Check wallet exists
check_wallet() {
    if [ ! -f "$WALLET_FILE" ]; then
        echo "❌ No wallet found. Run ./setup.sh first."
        exit 1
    fi
}

# Check solana CLI
check_solana() {
    if ! command -v solana-keygen &> /dev/null; then
        echo "❌ Solana CLI not found. Run ./setup.sh first."
        exit 1
    fi
}

case "$1" in
    address)
        check_wallet
        check_solana
        solana-keygen pubkey "$WALLET_FILE"
        ;;
    
    balance)
        check_wallet
        check_solana
        ADDRESS=$(solana-keygen pubkey "$WALLET_FILE")
        echo "📍 Address: $ADDRESS"
        echo ""
        
        # Try to get balance
        if command -v solana &> /dev/null; then
            echo "💰 Balance:"
            solana balance "$ADDRESS" --url "$RPC_URL" 2>/dev/null || \
                echo "   (Could not fetch balance - check network)"
        else
            echo "💰 Check balance at:"
            echo "   https://solscan.io/account/$ADDRESS"
        fi
        ;;
    
    export)
        check_wallet
        echo "⚠️  PRIVATE KEY - DO NOT SHARE!"
        echo ""
        
        # Try Python first (most reliable)
        if command -v python3 &> /dev/null; then
            python3 -c "
import json
import sys

# Base58 alphabet
ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

def base58_encode(data):
    num = int.from_bytes(data, 'big')
    result = ''
    while num > 0:
        num, rem = divmod(num, 58)
        result = ALPHABET[rem] + result
    for byte in data:
        if byte == 0:
            result = '1' + result
        else:
            break
    return result

try:
    with open('$WALLET_FILE', 'r') as f:
        keypair = json.load(f)
    private_key = bytes(keypair)
    bs58_key = base58_encode(private_key)
    print('Base58 Private Key (for Phantom):')
    print(bs58_key)
    print()
    print('To import in Phantom:')
    print('1. Open Phantom → Settings → Manage Accounts')
    print('2. Add/Connect Wallet → Import Private Key')
    print('3. Paste the Base58 key above')
except Exception as e:
    print(f'Error: {e}')
    sys.exit(1)
"
        else
            # Fallback: show raw keypair
            echo "Raw keypair array (install Python for Phantom format):"
            cat "$WALLET_FILE"
            echo ""
            echo ""
            echo "To convert to Phantom format:"
            echo "1. Go to https://www.base58.online/"
            echo "2. Paste the array and convert to Base58"
        fi
        ;;
    
    fund)
        check_wallet
        check_solana
        ADDRESS=$(solana-keygen pubkey "$WALLET_FILE")
        echo "📍 Send SOL to: $ADDRESS"
        echo ""
        echo "You need SOL for transaction fees (~0.02 SOL per launch)."
        echo ""
        echo "Options:"
        echo "  • Send from your exchange (Coinbase, Binance, etc.)"
        echo "  • Send from Phantom or another wallet"
        echo "  • Use a faucet for testnet (devnet only)"
        echo ""
        echo "View wallet: https://solscan.io/account/$ADDRESS"
        ;;
    
    check)
        check_wallet
        check_solana
        ADDRESS=$(solana-keygen pubkey "$WALLET_FILE")
        
        # Check remaining launches
        echo "📊 Checking status..."
        RESPONSE=$(curl -s "https://www.mintyouragent.com/api/launch?agent=$ADDRESS" 2>/dev/null)
        
        if echo "$RESPONSE" | grep -q '"launchesRemaining"'; then
            REMAINING=$(echo "$RESPONSE" | grep -o '"launchesRemaining":[0-9]*' | cut -d':' -f2)
            LIMIT=$(echo "$RESPONSE" | grep -o '"launchLimit":[0-9]*' | cut -d':' -f2)
            TODAY=$(echo "$RESPONSE" | grep -o '"launchesToday":[0-9]*' | cut -d':' -f2)
            TIER=$(echo "$RESPONSE" | grep -o '"tier":"[^"]*"' | cut -d'"' -f4)
            echo "👤 Tier: $TIER"
            echo "🚀 Launches today: $TODAY/$LIMIT"
            echo "📊 Remaining: $REMAINING"
        else
            echo "   Could not fetch launch stats"
        fi
        ;;
    
    *)
        echo "MintYourAgent Wallet"
        echo ""
        echo "Usage: ./wallet.sh <command>"
        echo ""
        echo "Commands:"
        echo "  address   Show wallet address"
        echo "  balance   Show SOL balance"
        echo "  export    Export private key for Phantom"
        echo "  fund      Get funding instructions"
        echo "  check     Check launch limit status"
        ;;
esac
