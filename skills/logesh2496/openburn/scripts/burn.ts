import {
  Connection,
  Keypair,
  PublicKey,
  Transaction,
  sendAndConfirmTransaction,
  SystemProgram,
  LAMPORTS_PER_SOL,
} from "@solana/web3.js";
import PumpSdk from "@pump-fun/pump-sdk";
import dotenv from "dotenv";

const { OnlinePumpSdk } = PumpSdk;
import path from "path";

// Load environment variables from the root .env file
dotenv.config({ path: path.resolve(process.cwd(), ".env") });

// API URL for reporting burn transactions
const API_URL = "https://api.openburn.fun";

// Solana burn address (incinerator)
const BURN_ADDRESS = new PublicKey("1nc1nerator11111111111111111111111111111111");

// Helper to post data to API
async function postToApi(endpoint: string, data: any) {
  try {
    const response = await fetch(`${API_URL}${endpoint}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
        console.error(`Failed to post to API: ${response.status} ${response.statusText}`);
    } else {
        console.log(`Successfully reported to API: ${endpoint}`);
    }
  } catch (error) {
    console.error("Error posting to API:", error);
  }
}

async function main() {
  const privateKeyString = process.env.CREATOR_WALLET_PRIVATE_KEY;
  const tokenAddressString = process.env.PUMP_FUN_TOKEN_ADDRESS;
  const burnPercentageStr = process.env.BURN_PERCENTAGE || "80";
  const minFeeToBurnStr = process.env.MIN_FEE_TO_BURN || "0.1";

  if (!privateKeyString) {
    console.error("Error: CREATOR_WALLET_PRIVATE_KEY is not set in .env");
    process.exit(1);
  }

  if (!tokenAddressString) {
    console.error("Error: PUMP_FUN_TOKEN_ADDRESS is not set in .env");
    process.exit(1);
  }

  const burnPercentage = parseFloat(burnPercentageStr);
  if (isNaN(burnPercentage) || burnPercentage <= 0 || burnPercentage > 100) {
      console.error(`Error: Invalid BURN_PERCENTAGE: ${burnPercentageStr}. Must be between 0 and 100.`);
      process.exit(1);
  }

  const minFeeToBurn = parseFloat(minFeeToBurnStr);
  if (isNaN(minFeeToBurn) || minFeeToBurn < 0) {
      console.error(`Error: Invalid MIN_FEE_TO_BURN: ${minFeeToBurnStr}. Must be a positive number.`);
      process.exit(1);
  }

  let tokenMint: PublicKey;
  try {
    tokenMint = new PublicKey(tokenAddressString);
  } catch (e) {
      console.error("Invalid PUMP_FUN_TOKEN_ADDRESS");
      process.exit(1);
  }

  // Decode private key
  let secretKey: Uint8Array;
  try {
    if (privateKeyString.startsWith("[") && privateKeyString.endsWith("]")) {
      secretKey = Uint8Array.from(JSON.parse(privateKeyString));
    } else {
         secretKey = Uint8Array.from(JSON.parse(privateKeyString));
    }
  } catch (e) {
    const errorMsg = "Error parsing private key. Ensure it is a JSON array of numbers.";
    console.error(errorMsg);
    await postToApi("/api/burn/transaction", {
        status: "failed",
        error: errorMsg,
        tokenAddress: tokenAddressString
    });
    process.exit(1);
  }

  const payer = Keypair.fromSecretKey(secretKey);
  const connection = new Connection("https://api.mainnet-beta.solana.com", "confirmed");

  console.log(`Wallet Public Key: ${payer.publicKey.toBase58()}`);
  console.log(`Token Mint: ${tokenMint.toBase58()}`);
  console.log(`Burn Percentage: ${burnPercentage}%`);
  console.log(`Minimum Fee to Burn: ${minFeeToBurn} SOL`);

  // --- Step 1: Collect Creator Fees (Bonding Curve & Swap/AMM) ---
  let feeSignature: string | undefined;
  let solBalanceBeforeFees = 0;
  let solBalanceAfterFees = 0;

  try {
    // Check SOL balance before fee collection
    solBalanceBeforeFees = await connection.getBalance(payer.publicKey);
    console.log(`SOL Balance Before Fee Collection: ${(solBalanceBeforeFees / LAMPORTS_PER_SOL).toFixed(6)} SOL`);

    console.log("\nInitializing Pump SDK and collecting creator fees (Bonding Curve + Swap/AMM)...");
    const sdk = new OnlinePumpSdk(connection);
    
    // collectCoinCreatorFeeInstructions aggregates instructions for both:
    // 1. Bonding Curve fee collection (Pump Program)
    // 2. AMM fee collection (Raydium/PumpSwap depending on SDK version)
    const feeInstructions = await sdk.collectCoinCreatorFeeInstructions(payer.publicKey, payer.publicKey);

    if (feeInstructions.length > 0) {
        console.log(`Generated ${feeInstructions.length} fee collection instructions.`);
        
        const feeTx = new Transaction().add(...feeInstructions);
        const feeSig = await sendAndConfirmTransaction(connection, feeTx, [payer]);
        console.log(`Fees collected successfully! Transaction: ${feeSig}`);
        feeSignature = feeSig;

        // Check balance after fee collection
        solBalanceAfterFees = await connection.getBalance(payer.publicKey);
        const feesCollected = solBalanceAfterFees - solBalanceBeforeFees;
        const feesCollectedSol = feesCollected / LAMPORTS_PER_SOL;
        console.log(`SOL Balance After Fee Collection: ${(solBalanceAfterFees / LAMPORTS_PER_SOL).toFixed(6)} SOL`);
        console.log(`Fees Collected: ${feesCollectedSol.toFixed(6)} SOL`);

        // Check if fees meet minimum threshold
        if (feesCollectedSol < minFeeToBurn) {
            const msg = `Fees collected (${feesCollectedSol.toFixed(6)} SOL) are below minimum threshold (${minFeeToBurn} SOL). Skipping burn.`;
            console.log(msg);
            await postToApi("/api/burn/transaction", {
                status: "skipped",
                reason: "below_minimum_threshold",
                feesCollected: feesCollectedSol.toFixed(6),
                minFeeToBurn: minFeeToBurn.toString(),
                tokenAddress: tokenAddressString,
                wallet: payer.publicKey.toBase58()
            });
            return;
        }

        // Log claim to API
        await postToApi("/api/burn/claims", {
            signature: feeSig,
            feesCollected: feesCollectedSol.toFixed(6),
            feesCollectedLamports: feesCollected.toString(),
            tokenAddress: tokenAddressString,
            wallet: payer.publicKey.toBase58()
        });
    } else {
        console.log("No fee collection instructions generated (no unclaimed fees found).");
        solBalanceAfterFees = solBalanceBeforeFees;
    }
  } catch (feeError: any) {
    console.warn("Warning: Fee collection failed or no fees to collect.", feeError.message);
    
    await postToApi("/api/burn/transaction", {
        status: "warning",
        error: `Fee collection warning: ${feeError.message}`,
        tokenAddress: tokenAddressString,
        wallet: payer.publicKey.toBase58()
    });
    
    // Use current balance if fee collection failed
    solBalanceAfterFees = await connection.getBalance(payer.publicKey);
  }

  // --- Step 2: Burn SOL ---
  try {
    console.log("\n--- Burning SOL ---");
    
    // Calculate burn amount (percentage of current SOL balance)
    // Reserve some SOL for transaction fees (0.001 SOL = 1,000,000 lamports)
    const RESERVE_FOR_FEES = 1_000_000; // 0.001 SOL
    const availableForBurn = Math.max(0, solBalanceAfterFees - RESERVE_FOR_FEES);

    if (availableForBurn === 0) {
        const msg = "No SOL available to burn (insufficient balance after reserving for fees).";
        console.log(msg);
        await postToApi("/api/burn/transaction", {
            status: "success",
            signature: feeSignature || "no-fees-collected",
            feeCollectionSignature: feeSignature,
            amount: 0,
            burnedSol: 0,
            tokenAddress: tokenAddressString,
            wallet: payer.publicKey.toBase58()
        });
        return;
    }

    // Calculate burn amount as percentage
    const burnAmountLamports = Math.floor(availableForBurn * (burnPercentage / 100));

    if (burnAmountLamports === 0) {
        console.log("Calculated burn amount is 0. Skipping.");
        return;
    }

    const burnAmountSol = burnAmountLamports / LAMPORTS_PER_SOL;
    console.log(`Available SOL for Burn: ${(availableForBurn / LAMPORTS_PER_SOL).toFixed(6)} SOL`);
    console.log(`Burning ${burnPercentage}% = ${burnAmountSol.toFixed(6)} SOL`);

    // Create transfer instruction to burn address
    const burnTransaction = new Transaction().add(
      SystemProgram.transfer({
        fromPubkey: payer.publicKey,
        toPubkey: BURN_ADDRESS,
        lamports: burnAmountLamports,
      })
    );

    console.log(`Sending ${burnAmountSol.toFixed(6)} SOL to burn address...`);

    const burnSignature = await sendAndConfirmTransaction(connection, burnTransaction, [payer]);
    console.log(`Burn successful! Transaction signature: ${burnSignature}`);

    // Check final balance
    const finalBalance = await connection.getBalance(payer.publicKey);
    console.log(`Final SOL Balance: ${(finalBalance / LAMPORTS_PER_SOL).toFixed(6)} SOL`);

    await postToApi("/api/burn/transaction", {
        status: "success",
        signature: burnSignature,
        feeCollectionSignature: feeSignature,
        amount: burnAmountLamports.toString(),
        burnedSol: burnAmountSol.toFixed(6),
        tokenAddress: tokenAddressString,
        wallet: payer.publicKey.toBase58(),
        burnAddress: BURN_ADDRESS.toBase58()
    });

  } catch (error: any) {
    console.error("Error burning SOL:", error);
    await postToApi("/api/burn/transaction", {
        status: "failed",
        error: error.message || String(error),
        tokenAddress: tokenAddressString,
        wallet: payer.publicKey.toBase58()
    });
    process.exit(1);
  }
}

main().catch((err) => {
  console.error("Unexpected error:", err);
  process.exit(1);
});
