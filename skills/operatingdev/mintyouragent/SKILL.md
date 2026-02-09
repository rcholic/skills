---
name: mintyouragent
description: Launch Solana tokens autonomously. Pure Python CLI - no bash/jq/solana-cli needed. Works on Windows, Mac, Linux. Use when you want to deploy a token on Solana.
---

# MintYourAgent

Launch Solana tokens. Free. You keep all creator fees.

📚 **Full docs**: https://www.mintyouragent.com/for-agents

---

## Quick Commands (Copy-Paste Ready)

### First Time Setup
```bash
pip install solders requests
python mya.py setup
```

### Before Your First Launch
```bash
# Show helpful pre-launch tips
python mya.py launch --tips

# Check your balance
python mya.py wallet balance

# Check your daily launch limit
python mya.py wallet check

# Test a launch (no SOL spent)
python mya.py launch --dry-run --name "Test" --symbol "TST" --description "Test" --image "https://..."
```

### "What's my wallet address?"
```bash
python mya.py wallet address
```

### "What's my private key?"
```bash
python mya.py wallet export
```
⚠️ Never share this with anyone!

### "How much SOL do I have?"
```bash
python mya.py wallet balance
```

### "How do I fund my wallet?"
```bash
python mya.py wallet fund
```

### "Launch a token"
```bash
python mya.py launch \
  --name "Token Name" \
  --symbol "TICKER" \
  --description "Description here" \
  --image "https://example.com/image.png"
```

### "Test a launch without spending SOL"
```bash
python mya.py launch --dry-run \
  --name "Test" \
  --symbol "TEST" \
  --description "Test token" \
  --image "https://example.com/img.png"
```

### "How many launches do I have left today?"
```bash
python mya.py wallet check
```

### "Delete my wallet and start fresh"
```bash
python mya.py uninstall --yes
python mya.py setup
```

---

## ⚠️ Auto-Launch Mode (RISKY)

Allows the AI to launch tokens WITHOUT asking permission each time.

### Enable (User must explicitly request this)
```bash
python mya.py config autonomous true
```

### Check if enabled
```bash
python mya.py config autonomous
```

### Disable
```bash
python mya.py config autonomous false
```

**RISKS:**
- AI may misinterpret context and launch unwanted tokens
- Each launch costs ~0.02 SOL in fees
- Tokens are permanent and public
- Could drain wallet if left unchecked

**Only enable if the user explicitly says:**
- "You can launch tokens on your own"
- "I trust you to launch autonomously"
- "Go ahead and mint whenever you see an opportunity"

---

## Launch Parameters

| Param | Required | Description |
|-------|----------|-------------|
| `--name` | ✅ | Token name (max 32 chars) |
| `--symbol` | ✅ | Ticker (max 10 chars, ASCII letters/numbers only) |
| `--description` | ✅ | What the token is about (max 1000 chars) |
| `--image` | ✅ | Image URL (HTTPS only) |
| `--image-file` | alt | Local image path (max 5MB) |
| `--banner` | ❌ | Banner image URL (HTTPS) |
| `--banner-file` | alt | Local banner path (max 5MB) |
| `--twitter` | ❌ | Twitter/X link (HTTPS) |
| `--telegram` | ❌ | Telegram link (HTTPS) |
| `--website` | ❌ | Website link (HTTPS) |
| `--initial-buy` | ❌ | Initial buy amount in SOL (default: 0) |
| `--slippage` | ❌ | Slippage in basis points (100 = 1%, default: 100) |
| `--dry-run` | ❌ | Test without launching |

### Example with Initial Buy

```bash
python mya.py launch \
  --name "My Token" \
  --symbol "MYT" \
  --description "Description here" \
  --image "https://example.com/image.png" \
  --initial-buy 0.5 \
  --slippage 200
```
This launches the token AND buys 0.5 SOL worth with 2% slippage tolerance.

### Let AI Decide Initial Buy

```bash
python mya.py launch \
  --name "My Token" \
  --symbol "MYT" \
  --description "Description here" \
  --image "https://example.com/image.png" \
  --ai-initial-buy
```
AI calculates initial buy based on wallet balance:
- Reserves 0.05 SOL for fees/future launches
- Uses ~15% of available balance
- Caps at 1 SOL max to limit risk
- Minimum 0.01 SOL if buying

---

## 🤖 AI Agent Guidelines

### Before First Launch - Ask the Human:
1. "Would you like me to show you some useful commands first?" → `python mya.py launch --tips`
2. "Should I check your wallet balance?" → `python mya.py wallet balance`
3. "Would you like to do a dry run first?" → `python mya.py launch --dry-run ...`

### Initial Buy Decision
When launching a token, ask the human:

> "Would you like to set an initial buy amount, or should I decide based on your balance?"
> 
> Options:
> - **You decide:** "Buy 0.5 SOL worth" → `--initial-buy 0.5`
> - **AI decides:** "You decide" → `--ai-initial-buy`
> - **No initial buy:** "Just launch, no buy" → (no flag)

### AI Decision Logic (--ai-initial-buy)
- Reserve 0.05 SOL for network fees + future launches
- Use 15% of remaining balance
- Maximum 1 SOL (risk management)
- Minimum 0.01 SOL if buying at all
- If balance < 0.06 SOL, no initial buy

### Risk Warnings to Share
- Initial buys are irreversible
- Token price can drop immediately after launch
- Only buy what you're willing to lose
- Consider doing a dry run first

---

## Economics

- **Platform fee:** FREE
- **Network fee:** ~0.02 SOL per launch
- **Creator fees:** You keep 100%
- **Daily limit:** 100 launches

---

## Troubleshooting

| Error | Fix |
|-------|-----|
| "Missing dependencies" | `pip install solders requests` |
| "No wallet found" | `python mya.py setup` |
| "Insufficient balance" | Send SOL to your wallet address |
| "Symbol must be alphanumeric" | Use only A-Z, 0-9 in symbol |
| "Network error" | Check internet connection |

---

## Security Notes

- **Data directory:** `~/.mintyouragent/` (not the skill folder)
- **wallet.json:** Stored with 600 permissions, verified on every load, checksum verified
- **SEED_PHRASE.txt:** Backup in ~/.mintyouragent/, never in public skill dir
- **SSL verification:** Enabled by default for all API calls
- **Local signing:** Private keys NEVER leave your machine ✅
- **Audit logging:** All operations logged to `~/.mintyouragent/audit.log`

### Environment Variables

| Variable | Description |
|----------|-------------|
| `MYA_API_URL` | Override API endpoint |
| `MYA_API_KEY` | API key for signed requests |
| `MYA_SSL_VERIFY` | Set to `false` to disable SSL (not recommended) |
| `HELIUS_RPC` | Custom Solana RPC endpoint |

### New Flags (v2.2.0)

| Flag | Description |
|------|-------------|
| `--json` | Output as JSON (for scripting) |
| `-v, --verbose` | Verbose logging |
| `-y, --yes` | Skip confirmation prompts |

### Secure Key Import

```bash
# GOOD: Read key from file (not visible in ps aux)
python mya.py wallet import < keyfile.txt

# AVOID: Passing key as argument (visible in process list)
python mya.py wallet import --key ABC123...
```

### Security Architecture

**Secure Local Signing Flow:**
1. CLI sends token metadata + your PUBLIC address to API
2. Server builds unsigned transaction, returns it
3. CLI verifies transaction (blockhash, signer)
4. CLI signs transaction LOCALLY with your private key
5. CLI submits signed transaction to server
6. Server broadcasts to Solana network

✅ **Your private key NEVER leaves your machine**

**Additional protections:**
- Transaction verification before signing (blockhash, expected signer)
- Replay attack protection via timestamps
- All URLs validated (HTTPS only, no SSRF)
- File size limits (5MB max for images)
- ASCII-only symbols (no Unicode lookalikes)
- File locking to prevent race conditions
- Secure deletion (overwrite before unlink)
- Memory clearing after key use
- Retry logic with exponential backoff
- Wallet integrity checksums
