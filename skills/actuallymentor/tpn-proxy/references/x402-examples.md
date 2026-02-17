# TPN x402 Code Examples (Pay-Per-Request with USDC on Base)

Working examples for generating a SOCKS5 proxy via `POST /api/v1/x402/proxy/generate` using the x402 payment protocol. No API key needed — pay with USDC on Base.

> These examples show the full x402 payment handshake for each language. For credential management best practices, see the [x402 specification](https://www.x402.org). The examples below load signing credentials from environment variables.

The flow for every language is the same:
1. Send request without payment
2. Receive `HTTP 402` with a `payment-required` header
3. Sign a USDC payment on Base using the decoded requirements
4. Retry the request with the payment signature
5. Receive SOCKS5 proxy credentials

---

## curl (step-by-step)

```bash
# Step 1: Send the initial request — expect a 402
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST \
  https://api.taoprivatenetwork.com/api/v1/x402/proxy/generate \
  -H "Content-Type: application/json" \
  -d '{"minutes": 60, "format": "json", "connection_type": "any"}')

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')

echo "Status: $HTTP_CODE"
echo "Body: $BODY"

# Step 2: Extract the payment-required header
# (use -i to see headers, or -D to dump them)
HEADERS=$(curl -s -D - -o /dev/null -X POST \
  https://api.taoprivatenetwork.com/api/v1/x402/proxy/generate \
  -H "Content-Type: application/json" \
  -d '{"minutes": 60, "format": "json", "connection_type": "any"}')

PAYMENT_REQUIRED=$(echo "$HEADERS" | grep -i 'payment-required' | cut -d' ' -f2- | tr -d '\r')
echo "Payment header (base64): $PAYMENT_REQUIRED"

# Decode to see the payment requirements
echo "$PAYMENT_REQUIRED" | base64 -d | jq .

# Steps 3-4: Sign and retry — curl alone can't sign EVM transactions.
# Use Node.js or Python below for the full automated flow.
# Once you have the payment signature, retry with:
#
# curl -s -X POST https://api.taoprivatenetwork.com/api/v1/x402/proxy/generate \
#   -H "Content-Type: application/json" \
#   -H "X-PAYMENT: <payment-signature>" \
#   -d '{"minutes": 60, "format": "json", "connection_type": "any"}'
```

---

## Browser JavaScript (ethers + fetch)

```bash
npm install ethers
```

```js
import { ethers } from 'ethers'

// EIP-712 domain and types for USDC permit on Base
const USDC_ADDRESS = '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913'
const url = 'https://api.taoprivatenetwork.com/api/v1/x402/proxy/generate'
const body = JSON.stringify( { minutes: 60, format: 'json', connection_type: 'any' } )

// Step 1: Send request without payment
const initial = await fetch( url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body
} )

if ( initial.status !== 402 ) throw new Error( `Expected 402, got ${ initial.status }` )

// Step 2: Decode payment requirements from the header
const payment_header = initial.headers.get( 'payment-required' )
const payment_requirements = JSON.parse( atob( payment_header ) )

console.log( 'Payment required:', payment_requirements )

const accept = payment_requirements.accepts[ 0 ]
const pay_to = accept.payTo
const amount = accept.amount // USDC base units (6 decimals)

// Step 3: Sign USDC payment on Base
// Requires a browser wallet (MetaMask etc.) connected to Base
const provider = new ethers.BrowserProvider( window.ethereum )
const signer = await provider.getSigner()

const usdc = new ethers.Contract( USDC_ADDRESS, [
    'function approve(address spender, uint256 amount) returns (bool)',
    'function allowance(address owner, address spender) view returns (uint256)'
], signer )

// Approve the payment amount
const tx = await usdc.approve( pay_to, amount )
await tx.wait()

// Sign the x402 payment attestation
const payment_message = {
    url,
    amount,
    payTo: pay_to,
    network: accept.network
}
const signature = await signer.signMessage( JSON.stringify( payment_message ) )

// Step 4: Retry with payment
const paid_response = await fetch( url, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-PAYMENT': signature
    },
    body
} )

const proxy_data = await paid_response.json()
const { username, password, ip_address, port } = proxy_data.vpnConfig
console.log( `Proxy: socks5h://${ username }:${ password }@${ ip_address }:${ port }` )
console.log( `Expires: ${ proxy_data.expiresAt }` )
```

---

## Node.js (@x402/core + @x402/evm)

The `@x402` libraries handle the full payment handshake automatically.

```bash
npm install @x402/core @x402/evm ethers
```

```js
import { x402Client } from '@x402/core/client'
import { x402HTTPClient } from '@x402/core/http'
import { ExactEvmClient, toClientEvmSigner } from '@x402/evm'
import { ethers } from 'ethers'

// Set up a Base signer (must hold USDC)
const provider = new ethers.JsonRpcProvider( 'https://mainnet.base.org' )
const wallet = new ethers.Wallet( process.env.X402_SIGNER_KEY, provider )
const signer = toClientEvmSigner( wallet )

// Create the x402 HTTP client
const client = new x402Client().register( 'eip155:*', new ExactEvmClient( signer ) )
const http = new x402HTTPClient( client )

const url = 'https://api.taoprivatenetwork.com/api/v1/x402/proxy/generate'
const body = JSON.stringify( { minutes: 60, format: 'json', connection_type: 'any' } )

// Step 1: Initial request (no payment)
const unpaid = await fetch( url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body
} )

if ( unpaid.status === 402 ) {

    // Step 2: Parse the 402 response
    const payment_required = http.getPaymentRequiredResponse(
        ( name ) => unpaid.headers.get( name ),
        await unpaid.json()
    )

    // Step 3: Sign USDC payment on Base
    const payment_payload = await http.createPaymentPayload( payment_required )

    // Step 4: Retry with payment signature
    const paid = await fetch( url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            ...http.encodePaymentSignatureHeader( payment_payload )
        },
        body
    } )

    // Step 5: Parse proxy credentials
    const proxy_data = await paid.json()
    const { username, password, ip_address, port } = proxy_data.vpnConfig

    const proxy_uri = `socks5h://${ username }:${ password }@${ ip_address }:${ port }`
    console.log( `Proxy: ${ proxy_uri }` )
    console.log( `Expires: ${ proxy_data.expiresAt }` )
}
```

---

## Python (web3.py + requests)

```bash
pip install web3 requests
```

```python
import json
import os
import base64
import requests
from web3 import Web3

# Base mainnet RPC
w3 = Web3(Web3.HTTPProvider("https://mainnet.base.org"))
account = w3.eth.account.from_key(os.environ["X402_SIGNER_KEY"])

USDC_ADDRESS = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
url = "https://api.taoprivatenetwork.com/api/v1/x402/proxy/generate"
payload = {"minutes": 60, "format": "json", "connection_type": "any"}

# Step 1: Initial request (no payment)
initial = requests.post(
    url,
    headers={"Content-Type": "application/json"},
    json=payload,
)

assert initial.status_code == 402, f"Expected 402, got {initial.status_code}"

# Step 2: Decode payment requirements
payment_header = initial.headers["payment-required"]
payment_requirements = json.loads(base64.b64decode(payment_header))

accept = payment_requirements["accepts"][0]
pay_to = accept["payTo"]
amount = int(accept["amount"])  # USDC in base units (6 decimals)

print(f"Payment required: {amount / 1e6:.2f} USDC to {pay_to}")

# Step 3: Approve and sign USDC transfer on Base
usdc_abi = [
    {
        "name": "approve",
        "type": "function",
        "inputs": [
            {"name": "spender", "type": "address"},
            {"name": "amount", "type": "uint256"},
        ],
        "outputs": [{"name": "", "type": "bool"}],
    }
]

usdc = w3.eth.contract(address=USDC_ADDRESS, abi=usdc_abi)

# Build and sign approval transaction
approve_tx = usdc.functions.approve(pay_to, amount).build_transaction({
    "from": account.address,
    "nonce": w3.eth.get_transaction_count(account.address),
    "gas": 100_000,
    "maxFeePerGas": w3.to_wei(0.1, "gwei"),
    "maxPriorityFeePerGas": w3.to_wei(0.01, "gwei"),
})

signed_tx = account.sign_transaction(approve_tx)
tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
w3.eth.wait_for_transaction_receipt(tx_hash)

# Sign the payment attestation
payment_message = json.dumps({
    "url": url,
    "amount": str(amount),
    "payTo": pay_to,
    "network": accept["network"],
})

signature = account.sign_message(
    Web3.solidity_keccak(["string"], [payment_message])
)

# Step 4: Retry with payment signature
paid = requests.post(
    url,
    headers={
        "Content-Type": "application/json",
        "X-PAYMENT": signature.signature.hex(),
    },
    json=payload,
)

# Step 5: Parse proxy credentials
proxy_data = paid.json()
vpn = proxy_data["vpnConfig"]
proxy_uri = f"socks5h://{vpn['username']}:{vpn['password']}@{vpn['ip_address']}:{vpn['port']}"

print(f"Proxy: {proxy_uri}")
print(f"Expires: {proxy_data['expiresAt']}")
```

---

## Payment Reference

| Field    | Value                                        |
|----------|----------------------------------------------|
| Network  | Base (eip155:8453)                           |
| Currency | USDC (6 decimals)                            |
| Contract | `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` |
| Scheme   | exact (pay exact amount)                     |
| Timeout  | 300 seconds                                  |

## Links

- x402 Protocol: https://www.x402.org
- @x402 npm packages: https://www.npmjs.com/org/x402
- Base Network: https://base.org
- USDC on Base: https://developers.circle.com/stablecoins/usdc-on-base
