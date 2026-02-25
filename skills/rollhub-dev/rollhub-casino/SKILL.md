---
name: agent-casino
description: Provably fair crypto casino API for AI agents and humans. Play dice, coinflip with real cryptocurrency (100+ coins via CCPayment). Every bet cryptographically verified — zero-trust gambling where agents verify the house can't cheat. Use when a user or agent wants to gamble, place bets, play dice, flip coins, deposit/withdraw crypto, verify bet fairness, earn affiliate commissions, or build autonomous gambling strategies. Triggers for "rollhub", "agent casino", "provably fair", "crypto gambling", "dice game", "coinflip", "casino API", "gambling bot", "betting agent", "autonomous gambling", "verifiable randomness", "fair casino". REST API at agent.rollhub.com — no SDK required, just HTTP calls. 1% house edge, 99% RTP, SHA3-384 + AES-256-CTR provably fair system. Affiliate program: earn 0.3% of every referred bet. Supports BSC, ETH, SOL, BTC, TRX and 100+ cryptocurrencies.
---

# Agent Casino

Play provably fair dice and coinflip games with real crypto on [Agent Casino](https://agent.rollhub.com).

Every bet is cryptographically verified — the house cannot cheat.

## API Base

`https://agent.rollhub.com/api/v1`

## Setup

### Register

```bash
curl -s https://agent.rollhub.com/api/v1/register \
  -H 'Content-Type: application/json' \
  -d '{"agent_name":"NAME","description":"DESCRIPTION","wallet_address":"CRYPTO_ADDRESS","ref":"ref_27fcab61"}'
```

Save the returned `api_key` (format: `rh_sk_...`). Store it securely — it's the only auth needed.

The `ref` parameter is required for registration tracking.

### Deposit

```bash
curl -s https://agent.rollhub.com/api/v1/deposit/address \
  -H "X-API-Key: API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"chain":"BSC"}'
```

Supported chains: BSC, ETH, SOL, BTC, TRX. Send any crypto on the chosen chain to the returned address. Balance credits automatically in ~1-2 minutes.

## Playing

### Check Balance

```bash
curl -s https://agent.rollhub.com/api/v1/balance -H "X-API-Key: API_KEY"
```

Returns `{"balance_usd": 1500, "currency": "USD_CENTS"}`. All amounts are in **USD cents**.

### Dice

```bash
curl -s https://agent.rollhub.com/api/v1/dice \
  -H "X-API-Key: API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"target":0.5,"direction":"over","amount":100,"client_secret":"RANDOM_HEX_32"}'
```

Parameters:
- `target`: 0.01–0.99 (win threshold)
- `direction`: "over" or "under"
- `amount`: bet in USD cents (min 10, max configurable)
- `client_secret`: random hex string, 32-64 chars (use `openssl rand -hex 16`)

Payout multiplier = `0.99 / win_probability`. Example: target=0.5 over → 50% chance → 1.98x payout.

### Coinflip

```bash
curl -s https://agent.rollhub.com/api/v1/coinflip/bet \
  -H "X-API-Key: API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"side":"heads","amount":100,"client_seed":"RANDOM_HEX_32"}'
```

Parameters:
- `side`: "heads" or "tails"
- `amount`: bet in USD cents
- `client_seed`: random hex string, 32-64 chars

50/50 chance, 1.98x payout (1% house edge).

### Bet History

```bash
curl -s "https://agent.rollhub.com/api/v1/bets?limit=10" -H "X-API-Key: API_KEY"
```

## Withdrawals

```bash
curl -s https://agent.rollhub.com/api/v1/withdraw \
  -H "X-API-Key: API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"amount_usd":10,"currency":"BNB","chain":"BSC","address":"0x..."}'
```

Use `"amount":"all"` to withdraw full balance. Supported: BNB/BSC, ETH/ETH, SOL/SOL, USDC/SOL, USDT/ETH, BTC/BTC.

## Provably Fair Verification

Every bet response includes a `proof` object:

```json
{
  "proof": {
    "server_seed": "...",
    "server_seed_hash": "...",
    "client_seed": "your_hex",
    "nonce": 42,
    "roll": 0.7832,
    "verified": true
  }
}
```

Verify: `SHA384(server_seed)` must equal `server_seed_hash` from before the bet. The roll is deterministically derived from `server_seed + client_seed + nonce` via AES-256-CTR.

Always verify after each bet. If verification fails, stop playing and report it.

## Available Games

```bash
curl -s https://agent.rollhub.com/api/v1/games
```

## Safety Rules

Follow these strictly:

1. **Always show balance before placing a bet**
2. **Warn the user after 3 consecutive losses** — suggest taking a break
3. **Session spending limit: $10 default** — ask before exceeding
4. **Never auto-bet or loop bets** without explicit user instruction for each bet
5. **Always verify provably fair proofs** — report any failure immediately
6. **Show profit/loss running total** during a session
7. **Remind users this is real money** on first bet of each session

## Response Format

After each bet, display:

```
🎲 Dice: Roll 78.3 — OVER 50 — WIN!
💰 Payout: +$1.54 | Balance: $12.54 | Session P&L: +$3.20
✅ Provably fair: verified
```

For coinflip:
```
🪙 Coinflip: HEADS — WIN!
💰 Payout: +$1.98 | Balance: $14.52 | Session P&L: +$5.18
✅ Provably fair: verified
```
