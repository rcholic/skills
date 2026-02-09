#!/bin/bash
# MintYourAgent Uninstall Script

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "⚠️  This will remove:"
echo "   • $SKILL_DIR/wallet.json"
echo "   • $SKILL_DIR/config.json"
echo "   • $SKILL_DIR/SEED_PHRASE.txt"
echo ""

if [ "$1" != "-y" ] && [ "$1" != "--yes" ]; then
    read -p "Are you sure? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        echo "Cancelled."
        exit 0
    fi
fi

rm -f "$SKILL_DIR/wallet.json"
rm -f "$SKILL_DIR/config.json"
rm -f "$SKILL_DIR/SEED_PHRASE.txt"

echo ""
echo "✅ Cleanup complete."
echo "Skill files (mya.py, SKILL.md) remain."
