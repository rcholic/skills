---
name: openburn
description: Automates collecting Pump.fun creator fees and burning a percentage of the collected SOL. Use this skill when the user wants to set up a regular fee collection and SOL burning schedule for their Pump.fun tokens.
metadata:
  {
    "openclaw":
      {
        "emoji": "🔥",
        "requires":
          {
            "modules": ["@solana/web3.js", "tsx", "dotenv"],
            "binaries": ["node", "pnpm"],
            "env":
              [
                "CREATOR_WALLET_PRIVATE_KEY",
                "PUMP_FUN_TOKEN_ADDRESS",
                "BURN_PERCENTAGE",
                "MIN_FEE_TO_BURN",
              ],
          },
        "install":
          [
            {
              "id": "pnpm-solana",
              "kind": "npm",
              "module": "@solana/web3.js",
              "cmd": "pnpm add @solana/web3.js @pump-fun/pump-sdk tsx dotenv -w",
              "label": "Install dependencies",
            },
          ],
      },
  }
---

# Openburn

This skill helps users automate the collection of creator fees and burning of SOL on Pump.fun.

## How It Works

1. **Collect Creator Fees**: The script collects trading fees (in SOL) from both the bonding curve and AMM pools
2. **Burn SOL**: A configurable percentage of the collected SOL is burned by transferring it to Solana's incinerator address (`1nc1nerator11111111111111111111111111111111`)

## Setup Instructions

1.  **Request Credentials**:
    Ask the user for the following information:
    - `PUMP_FUN_TOKEN_ADDRESS` (The token address on Pump.fun)
    - `CREATOR_WALLET_PRIVATE_KEY` (The private key of the wallet to burn from)
    - `BURN_PERCENTAGE` (Percentage of SOL to burn after fee collection, default: 80)
    - `MIN_FEE_TO_BURN` (Minimum SOL fees required to proceed with burn, default: 0.1)

    > [!IMPORTANT]
    > Remind the user that their keys will be stored locally in the `.env` file.

2.  **Store Credentials**:
    Check if the `.env` file exists in the root directory.
    - If it exists, append the keys.
    - If not, create it.

    Format:

    ```env
    PUMP_FUN_TOKEN_ADDRESS=...
    CREATOR_WALLET_PRIVATE_KEY=...
    BURN_PERCENTAGE=80
    MIN_FEE_TO_BURN=0.1
    ```

3.  **Register Token**:
    Once the `PUMP_FUN_TOKEN_ADDRESS` is received and stored, register the token with the API.

    **Endpoint**: `POST https://api.openburn.fun/api/burn/register`
    **Body**:

    ```json
    {
      "tokenAddress": "<PUMP_FUN_TOKEN_ADDRESS>"
    }
    ```

    This registration step is required before scheduling the burn job.

4.  **Schedule Job**:
    Ask the user for the scheduling interval (default: every 2 hours).

    Use the `cron` tool to register a new job:
    - **Name**: `openburn-job`
    - **Schedule**: `{ "kind": "every", "everyMs": 7200000 }` (replace 7200000 with user's interval in ms)
    - **Session Target**: `isolated`
    - **Payload**:
      ```json
      {
        "kind": "agentTurn",
        "message": "Execute the openburn script to burn SOL tokens.",
        "deliver": true
      }
      ```

5.  **Report Schedule**:
    Make a POST request to report the scheduled job.

    **Endpoint**: `POST https://api.openburn.fun/api/burn/schedule`
    **Body**:

    ```json
    {
      "jobId": "openburn-job",
      "intervalMs": 7200000
    }
    ```

## Execution Instructions

When the cron job triggers (receiving the message "Execute the openburn script..."):

1.  **Execute the Script**:
    Run the burn script located at `skills/openburn/scripts/burn.ts`.

    ```bash
    node --import tsx skills/openburn/scripts/burn.ts
    ```

2.  **Report Results**:
    The script will automatically report transaction success/failure to `https://api.openburn.fun/api/burn/transaction`.
    You should also report the output (transaction signature) to the user in the chat.
