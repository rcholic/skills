# Kite AI Agent Smart Wallet Permissionless Protocol V2.0

## Telegram Wallet Control

Run your own Telegram bot to control Kite AI smart wallets.

## Local Setup

### 1. Install
```bash
git clone <repo>
cd kite-agent-wallet-v2
npm install
```

### 2. Configure
```bash
cp .env.example .env
# Edit .env with your values
```

### 3. Run
```bash
node telegram-bot.js
```

## .env Configuration

| Variable | Required | Description |
|----------|----------|-------------|
| PRIVATE_KEY | Yes | Your wallet private key |
| TELEGRAM_BOT_TOKEN | Yes | Bot token from @BotFather |
| RPC_URL | No | RPC URL (default: testnet) |
| CHAIN_ID | No | Chain ID (default: 2368) |

## Commands

- `/create` - Create wallet
- `/wallet` - Get address
- `/balance` - Check balance
- `/session add <addr> <limit>` - Add session key
- `/limit set <amount>` - Set limit
- `/send <addr> <amount>` - Send KITE
- `/help` - Help

## Network

- Testnet: Chain ID 2368, RPC https://rpc-testnet.gokite.ai

## Contracts

- Factory: `0x0fa9F878B038DE435b1EFaDA3eed1859a6Dc098a`
