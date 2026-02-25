# Kite AI Agent Smart Wallet Permissionless Protocol V2.0

## Architecture

Each user runs their own Telegram bot locally:
- User creates their own Telegram bot
- Bot runs on user's local machine
- User's private key stays on their machine
- OpenClaw provides the smart contracts

```
User's PC                        Kite AI Network
┌─────────────────┐              ┌──────────────┐
│ Telegram Bot    │◄────────────►│ Smart        │
│ (runs locally)  │   Commands   │ Contracts    │
│                 │              │              │
│ - Private Key  │              │ - Factory    │
│ - Bot Token    │              │ - Wallet     │
└─────────────────┘              └──────────────┘
```

## Quick Start

### 1. Create Your Telegram Bot
1. Open Telegram → @BotFather
2. Send `/newbot`
3. Get your **Bot Token**

### 2. Get Testnet KITE
- Faucet: https://faucet.gokite.ai

### 3. Run Bot Locally

```bash
# Clone
git clone <repo>
cd kite-agent-wallet-v2

# Install
npm install

# Configure
cp .env.example .env
# Edit .env:
#   PRIVATE_KEY=your_wallet_private_key
#   TELEGRAM_BOT_TOKEN=your_bot_token

# Run
node telegram-bot.js
```

## .env Configuration

```env
PRIVATE_KEY=0xyour_private_key_here
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
RPC_URL=https://rpc-testnet.gokite.ai
```

## Commands

| Command | Description |
|---------|-------------|
| `/create` | Create smart wallet |
| `/wallet` | Get wallet address |
| `/balance` | Check balance |
| `/session add <addr> <limit>` | Add session key |
| `/limit set <amount>` | Set spending limit |
| `/send <addr> <amount>` | Send KITE |
| `/help` | Help |

## Network

- **Testnet**: Chain ID 2368
- **RPC**: https://rpc-testnet.gokite.ai
- **Explorer**: https://testnet.kitescan.ai

## Deployed Contracts

| Contract | Address |
|----------|---------|
| AgentSmartWalletFactory | `0x0fa9F878B038DE435b1EFaDA3eed1859a6Dc098a` |

## Security

- Private key stays on your machine
- Only you control your wallet
- Session keys add extra security

## Version

- v2.0.2 (2026-02-25): User runs their own bot
- v2.0.1 (2026-02-25): Local deployment
- v2.0.0 (2026-02-25): Initial
- v1.0.0 (2026-02-25): Core contracts
