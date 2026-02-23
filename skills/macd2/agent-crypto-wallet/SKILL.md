---
name: agentwalletapi
description: OpenclawCash crypto wallet API for AI agents. Use when an agent needs to send native or token transfers, check balances, list wallets, or interact with EVM and Solana wallets programmatically via OpenclawCash.
license: Proprietary
compatibility: Requires network access to https://openclawcash.com
metadata:
  author: agentwalletapi
  version: "1.9.1"
  required_env_vars:
    - AGENTWALLETAPI_KEY
  optional_env_vars:
    - AGENTWALLETAPI_URL
  required_binaries:
    - curl
  optional_binaries:
    - jq
---

# OpenclawCash Agent API

Interact with OpenclawCash-managed wallets to send native assets and tokens, check balances, and execute agent-safe wallet operations across EVM and Solana networks.

## Requirements

- Required env var: `AGENTWALLETAPI_KEY`
- Optional env var: `AGENTWALLETAPI_URL` (default: `https://openclawcash.com`)
- Required local binary: `curl`
- Optional local binary: `jq` (for pretty JSON output in CLI)
- Network access required: `https://openclawcash.com`

## Safety Model

- Start with read-only calls (`wallets`, `wallet`, `balance`, `tokens`) on testnets first.
- High-risk actions are gated:
  - API key permissions in dashboard (`allowWalletCreation`, `allowWalletImport`)
  - Explicit CLI confirmation (`--yes`) for write actions

## Setup

1. Run the setup script to create your `.env` file:
   ```
   bash scripts/setup.sh
   ```
2. Edit the `.env` file in this skill folder and replace the placeholder with your real API key:
   ```
   AGENTWALLETAPI_KEY=ag_your_real_key_here
   ```
3. Get your API key at https://openclawcash.com (sign up, create a wallet, go to API Keys page).

## CLI Tool

Use the included tool script to make API calls directly:

```bash
# Read-only (recommended first)
bash scripts/agentwalletapi.sh wallets
bash scripts/agentwalletapi.sh wallet 2
bash scripts/agentwalletapi.sh wallet "Trading Bot"
bash scripts/agentwalletapi.sh balance 2
bash scripts/agentwalletapi.sh transactions 2
bash scripts/agentwalletapi.sh tokens mainnet

# Write actions (require explicit --yes)
bash scripts/agentwalletapi.sh create "Ops Wallet" sepolia --yes
bash scripts/agentwalletapi.sh import "Treasury Imported" mainnet --yes
# Automation-safe import: read private key from stdin instead of command args
printf '%s' '<private_key>' | bash scripts/agentwalletapi.sh import "Treasury Imported" mainnet - --yes
bash scripts/agentwalletapi.sh transfer 2 0xRecipient 0.01 --yes
bash scripts/agentwalletapi.sh transfer 2 0xRecipient 100 USDC --yes
bash scripts/agentwalletapi.sh quote mainnet WETH USDC 10000000000000000
bash scripts/agentwalletapi.sh swap 2 WETH USDC 10000000000000000 0.5 --yes
```

### Import Input Safety

- Wallet import is optional and not required for normal wallet operations (list, balance, transfer, swap).
- Import works only when the user explicitly enables API key permission `allowWalletImport` in dashboard settings.
- Import execution requires explicit confirmation in the CLI (`--yes` for automation, or interactive `YES` prompt).
- Avoid passing sensitive inputs as CLI arguments when possible (shell history/process logs risk).
- Preferred options:
  - Interactive hidden prompt: omit the private key argument.
  - Automation: pass `-` and pipe input via stdin.

## Base URL

```
https://openclawcash.com
```

## Troubleshooting

If requests fail because of host/URL issues, use this recovery flow:

1. Open `agentwalletapi/.env` and verify `AGENTWALLETAPI_KEY` is set and has no extra spaces.
2. If the API host is wrong or unreachable, set this in the same `.env` file:
   ```
   AGENTWALLETAPI_URL=https://openclawcash.com
   ```
3. Retry a simple read call first:
   ```bash
   bash scripts/agentwalletapi.sh wallets
   ```
4. If it still fails, report the exact error and stop before attempting transfer/swap actions.

## Authentication

The API key is loaded from the `.env` file in this skill folder. For direct HTTP calls, include it as a header:

```
X-Agent-Key: ag_your_key_here
Content-Type: application/json
```

## API Surfaces

- **Agent API (API key auth):** `/api/agent/*`
  - Authenticate with `X-Agent-Key`
  - Used for autonomous agent execution (wallets list/create/import, transactions, balance, transfer, swap, quote, approve)
- **Dashboard/User API (session auth):** `/api/wallets/*`
  - Authenticate with bearer token or `aw_session` cookie
  - Used for user-managed dashboard operations (including wallet import and wallet creation).
  - Dashboard wallet creation now requires `exportPassphrase` (minimum 12 characters).
  - Private-key export requires `exportPassphrase` and is protected by rate limits and temporary lockouts.

## Workflow

1. `GET /api/agent/wallets` - Discover available wallets (id, label, address, network, chain; no balances)
2. `GET /api/agent/wallet?walletId=...` or `?walletLabel=...` - Fetch one wallet with native/token balances
3. Optional wallet lifecycle actions:
   - `POST /api/agent/wallets/create` - Create a new wallet under API-key policy controls
   - `POST /api/agent/wallets/import` - Import a `mainnet` or `solana-mainnet` wallet under API-key policy controls
4. `GET /api/agent/transactions?walletId=...` - Read merged wallet transaction history (on-chain + app-recorded)
5. `GET /api/agent/supported-tokens?network=...` or `?chain=evm|solana` - Get recommended common, well-known token list + guidance
6. `POST /api/agent/token-balance` - Check wallet balances (native + token balances; specific token by symbol/address supported)
7. `POST /api/agent/quote` - Get a Uniswap quote before execution (EVM only)
8. `POST /api/agent/swap` - Execute token swap on Uniswap (EVM) or Jupiter (Solana)
9. `POST /api/agent/transfer` - Send native coin or token on the wallet's chain (optional `chain` guard)
10. Use returned `txHash` values to confirm transactions

## Quick Reference

| Endpoint | Method | Auth | Purpose |
|---|---|---|---|
| `/api/agent/wallets` | GET | Yes | List wallets (discovery only, no balances) |
| `/api/agent/wallet` | GET | Yes | Get one wallet detail with native/token balances |
| `/api/agent/wallets/create` | POST | Yes | Create a new API-key-managed wallet |
| `/api/agent/wallets/import` | POST | Yes | Import a mainnet/solana-mainnet wallet via API key |
| `/api/agent/transactions` | GET | Yes | List per-wallet transaction history |
| `/api/agent/transfer` | POST | Yes | Send native/token transfers (EVM + Solana) |
| `/api/agent/swap` | POST | Yes | Execute DEX swap (Uniswap on EVM, Jupiter on Solana) |
| `/api/agent/quote` | POST | No | Get Uniswap quote (EVM only) |
| `/api/agent/token-balance` | POST | Yes | Check balances |
| `/api/agent/supported-tokens` | GET | No | List recommended common, well-known tokens per network |
| `/api/agent/approve` | POST | Yes | Approve spender for ERC-20 token (EVM only) |

## Agent Wallet Create/Import (Agent API)

Agent-side wallet lifecycle endpoints:

- `POST /api/agent/wallets/create`
- `POST /api/agent/wallets/import`

Behavior notes:
- Both require `X-Agent-Key`.
- Both are gated by API key permissions configured in dashboard:
  - `allowWalletCreation` for create
  - `allowWalletImport` for import
- Both are rate-limited per API key. Exceeding the limit returns `429` with `Retry-After`.
- Agent import supports `mainnet` and `solana-mainnet`.
- Agent wallet create requires:
  - `exportPassphrase` (minimum 12 characters)
  - `confirmExportPassphraseSaved: true`
- Agent-safe create sequence:
  - Save export passphrase in secure storage first.
  - Then call `POST /api/agent/wallets/create` with that passphrase and confirmation.

## Transfer Examples

Send native coin (default when no token specified):
```json
{ "walletId": 2, "to": "0xRecipient...", "amount": "0.01" }
```

Send 100 USDC by symbol:
```json
{ "walletLabel": "Trading Bot", "to": "0xRecipient...", "token": "USDC", "amount": "100" }
```

Send arbitrary ERC-20 by contract address:
```json
{ "walletId": 2, "to": "0xRecipient...", "token": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", "amount": "100" }
```

Send SOL by symbol:
```json
{ "walletId": "Q7X2K9P", "to": "SolanaRecipientWalletAddress...", "token": "SOL", "amount": "0.01" }
```

Send SOL with memo (Solana only):
```json
{ "walletId": "Q7X2K9P", "to": "SolanaRecipientWalletAddress...", "token": "SOL", "amount": "0.01", "memo": "payment verification note" }
```

Use `amount` for human-readable values (e.g., "100" = 100 USDC). Use `value` for base units (smallest denomination on each chain).
Use optional `chain: "evm" | "solana"` in agent payloads for explicit chain routing and validation.
`memo` is supported only for Solana transfers and must pass safety validation (max 5 words, max 256 UTF-8 bytes, no control/invisible characters).
For native SOL transfers, the API may auto-adjust requested value to fit platform fee + network fee.
Transfer responses include `requestedValue`, `adjustedValue`, `requestedAmount`, and `adjustedAmount`.

## Token Support Model

- `GET /api/agent/supported-tokens` returns recommended common, well-known tokens plus guidance fields.
- EVM transfer/swap/balance endpoints support **any valid ERC-20 token contract address**.
- Solana transfer/balance endpoints support **any valid SPL mint address**.
- Native tokens appear as `ETH` on EVM and `SOL` on Solana (with chain-specific native token IDs in balance payloads).

## Error Codes

- 200: Success
- 400: Invalid input, insufficient funds, unknown token, or policy violation
- 400 `chain_mismatch`: requested `chain` does not match the selected wallet
- 400 `insufficient_balance`: requested transfer + fees exceed available balance
- 401: Missing/invalid API key
- 404: Wallet not found
- 500: Internal error (retry with corrected payload or reduced amount)

## Policy Constraints

Wallets may have governance policies:
- **Whitelist**: Only transfers to pre-approved addresses allowed
- **Spending Limit**: Max value per transaction (configured per wallet policy)

Violations return HTTP 401 with an explanation message.

## Important Notes

- All POST requests require `Content-Type: application/json`
- EVM token transfers require ETH in the wallet for gas fees
- Solana token transfers require SOL in the wallet for fees
- Solana transfer memos are optional and Solana-only: max 5 words, max 256 UTF-8 bytes, no control/invisible characters
- Solana native transfers account for network fee and can auto-adjust requested transfer amount
- If requested native SOL + platform fee + network fee cannot fit wallet balance, API returns `400 insufficient_balance`
- Swap supports EVM (Uniswap) and Solana (Jupiter); Quote/Approve are EVM-only
- A platform fee (default 1%) is deducted from the token amount
- Use `amount` for simplicity, use `value` for precise base-unit control
- For robust agent behavior:
  - First call `wallets`, then `wallet` (or `token-balance`), then `quote`, then `swap`.
  - On 400 with `insufficient_token_balance`, reduce amount or change token.
- The `.env` file in this skill folder stores your API key — never commit it to version control

## File Structure

```
agentwalletapi/
├── SKILL.md                    # This file
├── .env                        # Your API key (created by setup.sh)
├── scripts/
│   ├── setup.sh                # Creates .env with API key placeholder
│   └── agentwalletapi.sh       # CLI tool for making API calls
└── references/
    └── api-endpoints.md        # Full endpoint documentation
```

See [references/api-endpoints.md](references/api-endpoints.md) for full endpoint details with request/response examples.
