#!/bin/bash
# ⚠️ DEPRECATED - Use Python version instead:
#    python mya.py launch --name "..." --symbol "..." --description "..." --image "..."

echo "⚠️  This script is deprecated. Use: python mya.py launch ..." >&2

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WALLET_FILE="$SKILL_DIR/wallet.json"
API_URL="https://www.mintyouragent.com/api/launch"

# Check wallet exists
if [ ! -f "$WALLET_FILE" ]; then
    echo "❌ No wallet found. Run ./setup.sh first."
    exit 1
fi

# Parse arguments
NAME=""
SYMBOL=""
DESCRIPTION=""
IMAGE=""
IMAGE_FILE=""
BANNER=""
BANNER_FILE=""
TWITTER=""
TELEGRAM=""
WEBSITE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --name) NAME="$2"; shift 2 ;;
        --symbol) SYMBOL="$2"; shift 2 ;;
        --description) DESCRIPTION="$2"; shift 2 ;;
        --image) IMAGE="$2"; shift 2 ;;
        --image-file) IMAGE_FILE="$2"; shift 2 ;;
        --banner) BANNER="$2"; shift 2 ;;
        --banner-file) BANNER_FILE="$2"; shift 2 ;;
        --twitter) TWITTER="$2"; shift 2 ;;
        --telegram) TELEGRAM="$2"; shift 2 ;;
        --website) WEBSITE="$2"; shift 2 ;;
        --help)
            echo "MintYourAgent Token Launcher"
            echo ""
            echo "Usage: ./launch.sh --name \"Name\" --symbol \"SYM\" --description \"Desc\" --image \"url\""
            echo ""
            echo "Required:"
            echo "  --name         Token name (max 32 chars)"
            echo "  --symbol       Token ticker (max 10 chars, alphanumeric)"
            echo "  --description  Token description (max 1000 chars)"
            echo "  --image        Image URL (or use --image-file)"
            echo "  --image-file   Local image path"
            echo ""
            echo "Optional:"
            echo "  --banner       Banner image URL (or use --banner-file)"
            echo "  --banner-file  Local banner path"
            echo "  --twitter      Twitter/X URL"
            echo "  --telegram     Telegram URL"
            echo "  --website      Website URL"
            exit 0
            ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

# Validate required fields
if [ -z "$NAME" ] || [ -z "$SYMBOL" ] || [ -z "$DESCRIPTION" ]; then
    echo "❌ Missing required fields: --name, --symbol, --description"
    echo "Run ./launch.sh --help for usage."
    exit 1
fi

if [ -z "$IMAGE" ] && [ -z "$IMAGE_FILE" ]; then
    echo "❌ Missing image: provide --image URL or --image-file path"
    exit 1
fi

# Validate symbol
if [ ${#SYMBOL} -gt 10 ]; then
    echo "❌ Symbol must be 10 characters or less"
    exit 1
fi

if ! echo "$SYMBOL" | grep -qE '^[A-Za-z0-9]+$'; then
    echo "❌ Symbol must be alphanumeric only"
    exit 1
fi

# Handle local image file - convert to base64 data URL
if [ -n "$IMAGE_FILE" ]; then
    if [ ! -f "$IMAGE_FILE" ]; then
        echo "❌ Image file not found: $IMAGE_FILE"
        exit 1
    fi
    MIME_TYPE=$(file -b --mime-type "$IMAGE_FILE")
    # Cross-platform base64 (macOS doesn't have -w flag)
    if base64 --help 2>&1 | grep -q '\-w'; then
        IMAGE="data:$MIME_TYPE;base64,$(base64 -w 0 "$IMAGE_FILE")"
    else
        IMAGE="data:$MIME_TYPE;base64,$(base64 "$IMAGE_FILE" | tr -d '\n')"
    fi
fi

# Handle local banner file - convert to base64 data URL
if [ -n "$BANNER_FILE" ]; then
    if [ ! -f "$BANNER_FILE" ]; then
        echo "❌ Banner file not found: $BANNER_FILE"
        exit 1
    fi
    BANNER_MIME=$(file -b --mime-type "$BANNER_FILE")
    if base64 --help 2>&1 | grep -q '\-w'; then
        BANNER="data:$BANNER_MIME;base64,$(base64 -w 0 "$BANNER_FILE")"
    else
        BANNER="data:$BANNER_MIME;base64,$(base64 "$BANNER_FILE" | tr -d '\n')"
    fi
fi

# Read keypair
KEYPAIR=$(cat "$WALLET_FILE")

# JSON escape function
json_escape() {
    printf '%s' "$1" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))'  2>/dev/null || \
    printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g; s/\t/\\t/g; s/\n/\\n/g; s/\r/\\r/g'
}

# Escape values for JSON
NAME_ESCAPED=$(json_escape "$NAME")
SYMBOL_ESCAPED=$(json_escape "$SYMBOL")
DESC_ESCAPED=$(json_escape "$DESCRIPTION")

# Remove surrounding quotes from python output if present
NAME_ESCAPED="${NAME_ESCAPED%\"}"
NAME_ESCAPED="${NAME_ESCAPED#\"}"
SYMBOL_ESCAPED="${SYMBOL_ESCAPED%\"}"
SYMBOL_ESCAPED="${SYMBOL_ESCAPED#\"}"
DESC_ESCAPED="${DESC_ESCAPED%\"}"
DESC_ESCAPED="${DESC_ESCAPED#\"}"

# Build JSON payload using jq if available, otherwise manual construction
if command -v jq &> /dev/null; then
    JSON_PAYLOAD=$(jq -n \
        --arg name "$NAME" \
        --arg symbol "$SYMBOL" \
        --arg description "$DESCRIPTION" \
        --arg image "$IMAGE" \
        --argjson keypair "$KEYPAIR" \
        '{name: $name, symbol: $symbol, description: $description, image: $image, keypair: $keypair}')
    
    [ -n "$BANNER" ] && JSON_PAYLOAD=$(echo "$JSON_PAYLOAD" | jq --arg banner "$BANNER" '. + {banner: $banner}')
    [ -n "$TWITTER" ] && JSON_PAYLOAD=$(echo "$JSON_PAYLOAD" | jq --arg twitter "$TWITTER" '. + {twitter: $twitter}')
    [ -n "$TELEGRAM" ] && JSON_PAYLOAD=$(echo "$JSON_PAYLOAD" | jq --arg telegram "$TELEGRAM" '. + {telegram: $telegram}')
    [ -n "$WEBSITE" ] && JSON_PAYLOAD=$(echo "$JSON_PAYLOAD" | jq --arg website "$WEBSITE" '. + {website: $website}')
else
    # Manual JSON construction with escaping
    JSON_PAYLOAD="{\"name\":\"$NAME_ESCAPED\",\"symbol\":\"$SYMBOL_ESCAPED\",\"description\":\"$DESC_ESCAPED\",\"image\":\"$IMAGE\",\"keypair\":$KEYPAIR"
    [ -n "$BANNER" ] && JSON_PAYLOAD="$JSON_PAYLOAD,\"banner\":\"$BANNER\""
    [ -n "$TWITTER" ] && JSON_PAYLOAD="$JSON_PAYLOAD,\"twitter\":\"$TWITTER\""
    [ -n "$TELEGRAM" ] && JSON_PAYLOAD="$JSON_PAYLOAD,\"telegram\":\"$TELEGRAM\""
    [ -n "$WEBSITE" ] && JSON_PAYLOAD="$JSON_PAYLOAD,\"website\":\"$WEBSITE\""
    JSON_PAYLOAD="$JSON_PAYLOAD}"
fi

echo "🚀 Launching token on pump.fun..."
echo "   Name: $NAME"
echo "   Symbol: $SYMBOL"
echo ""

# Make API request with timeout
RESPONSE=$(curl -s --max-time 120 -X POST "$API_URL" \
    -H "Content-Type: application/json" \
    -d "$JSON_PAYLOAD")

# Check curl exit code
if [ $? -ne 0 ]; then
    echo "❌ Network error: Could not reach API"
    exit 1
fi

# Check for success
if echo "$RESPONSE" | grep -q '"success":true'; then
    MINT=$(echo "$RESPONSE" | grep -o '"mint":"[^"]*"' | cut -d'"' -f4)
    PUMP_URL=$(echo "$RESPONSE" | grep -o '"pumpUrl":"[^"]*"' | cut -d'"' -f4)
    echo "✅ Token launched!"
    echo "🪙 Mint: $MINT"
    echo "🔗 $PUMP_URL"
else
    echo "❌ Launch failed:"
    echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
    exit 1
fi
