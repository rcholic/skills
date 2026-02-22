---
name: rsoft-agentic-bank
description: Provides real-time RSoft Agentic Bank services — credit checks, loan requests, and interest rate queries for autonomous agents.
version: 1.4.0
requires:
  bins:
    - curl
metadata:
  openclaw:
    homepage: https://rsoft-agentic-bank.com/
---

# RSoft Agentic Bank

Official skill for **RSoft Agentic Bank** — an AI-native lending service for autonomous agents in Latin America and beyond.

This skill connects to the RSoft Agentic Bank REST API using `curl` via the exec tool.

## Base URL

```
https://7mavs5vu7ggbhtxvbavdgs26qa0cbawg.lambda-url.us-east-1.on.aws
```

## Available Commands

### 1. Check Interest Rates

Query current lending rates for all risk tiers:

```bash
curl -s https://7mavs5vu7ggbhtxvbavdgs26qa0cbawg.lambda-url.us-east-1.on.aws/api/interest-rates
```

Returns: current rates by loan type, currency (USDC), network, and last update date.

### 2. Check Credit Score

Verify an agent's creditworthiness and repayment history:

```bash
curl -s https://7mavs5vu7ggbhtxvbavdgs26qa0cbawg.lambda-url.us-east-1.on.aws/api/creditworthiness/{agent_id}
```

Replace `{agent_id}` with the agent's unique identifier.

Returns: credit score (0-850), outstanding debt, repayment history, and status.

### 3. Request a Loan

Submit a loan request with AI-powered risk assessment:

```bash
curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{"agent_id": "your-agent-id", "amount": 5000}' \
  https://7mavs5vu7ggbhtxvbavdgs26qa0cbawg.lambda-url.us-east-1.on.aws/api/loans
```

Returns: approval status, transaction hash if approved, interest rate, and terms.

## Quick Start

1. Run the interest rates curl command to see current lending rates.
2. Run the creditworthiness curl command with your agent ID to check eligibility.
3. Run the loans curl command with the desired amount to request financing.
4. Visit [rsoft-agentic-bank.com](https://rsoft-agentic-bank.com/) for full documentation.

## Verification

- **Official Website:** [rsoft-agentic-bank.com](https://rsoft-agentic-bank.com/)
- **Publisher:** RSoft Latam
- **Protocol:** REST API via curl
- **Network:** Base (Coinbase L2)

---
*Developed by RSoft Latam — Empowering the Agentic Economy.*
