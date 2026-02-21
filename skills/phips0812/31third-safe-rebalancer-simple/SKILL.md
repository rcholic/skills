---
name: 31third-safe-rebalancer-simple
description: One-step Safe rebalancer using on-chain 31Third policies.
homepage: https://31third.com
---

# 31Third Safe Rebalancer Simple

This skill is intentionally minimal for non-technical users.

Best practice: use only one command / one tool:

- `rebalance_now`

If you are unsure, use the help command first:

- `npm run cli -- help`

## Prerequisites

- Node.js 22+
- npm

## Local Setup

```bash
npm install
npm run build
```

## Setup

1. Deploy your Safe + policies using the 31Third policy wizard:
   <https://app.31third.com/safe-policy-deployer>
2. You need at least two wallets:
   - Safe owner wallet: never share this private key.
   - Executor wallet: configured in the wizard on `ExecutorModule`; this private key is used by this skill.
3. Copy env vars from the final wizard overview.

Required env vars:

```bash
SAFE_ADDRESS=0xYourSafe
EXECUTOR_MODULE_ADDRESS=0xYourExecutorModule
EXECUTOR_WALLET_PRIVATE_KEY=0x...
TOT_API_KEY=your_31third_api_key
RPC_URL=https://mainnet.base.org
CHAIN_ID=8453
```

`TOT_API_KEY` can be requested via <https://31third.com/contact> or by emailing `dev@31third.com`.

## What rebalance_now does

1. Reads `AssetUniverse` and `StaticAllocation` policy state from `ExecutorModule`.
2. Builds `baseEntries` from current Safe balances for AssetUniverse tokens.
3. Builds `targetEntries` from on-chain StaticAllocation targets.
4. Calls SDK `calculateRebalancing(...)`.
5. Executes via SDK `executeRebalancing(...)` using ethers wallet signer.
6. Waits for confirmation and returns tx hash.

Safety checks:

- Fails if `scheduler != registry`.
- Fails if executor wallet is not equal to `registry`.
- Fails if required policies are missing.
- Loads `driftThresholdBps` from StaticAllocation and skips execution when drift is below threshold.
- Loads `maxSlippageBps` from SlippagePolicy and uses:
  - `maxSlippage = policySlippage - 0.1%`
  - `maxPriceImpact = policySlippage - 0.1%`
- Uses default `minTradeValue = 0.1`.

Partial policy deployment behavior:

- If AssetUniverse is not deployed, base entries default to `[]`.
- If SlippagePolicy is not deployed, configured/default slippage values are used.
- If StaticAllocation is not deployed, auto target fetch is not possible.
  This is the only fallback case where you should pass manual `targetEntries`.
  Do this only when StaticAllocation policy is intentionally not deployed.
  CLI fallback example:
  `npm run cli -- rebalance-now --target-entries '[{"tokenAddress":"0x...","allocation":0.5},{"tokenAddress":"0x...","allocation":0.5}]'`

## CLI

```bash
npm run cli -- help
npm run cli -- rebalance-now
npm run cli -- rebalance-now --target-entries '[{"tokenAddress":"0x...","allocation":0.5},{"tokenAddress":"0x...","allocation":0.5}]'
```
