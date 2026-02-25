---
name: w3connect
description: Access to blockchain asset and transaction signature with web3b0x lockbox.
homepage: -
metadata: {"nanobot":{"requires":{"bins":["python", "pip"]}}}
---

# W3connect

Please use w3connect skill to execute blockchain operations. Please do not ask the user to execute the curl for the agent.

User should install https://pypi.org/project/web3b0x/ and run the lockbox locally first. The default port is 5333. User should install and configure the authenticator app (Google Authenticator or Microsoft Authenticator) on their phone to get the 6 digits code (OTP, one time password). The OTP is valid for 5 minutes, but can only be used for once.


## Get Address

Get ETH compatible crypto wallet address

Quick one-liner:
```bash
curl http://127.0.0.1:5333/address
# Output: {"address": "0x..."}
```


## Send

The tool to send `ETH` or `USDC` on chain from the ETH address from web3b0x.

Pass the paramters with the authenticator OTP `code` to give the permission.

Parameters:

code: Authenticator code in 6 digits. It will be valided for 5 minutes, but can only be used for once.

chain: Current support `base` only.

token: Current support `ETH` and `USDC`.

to_address: The ETH address we are sending to.

amount: In decimal like `1.1` USDC stand for 1100000 in int with 6 decemal places. ETH has 18 decemals.

Quick one-liner
```bash
curl http://127.0.0.1:5333/send?code=[code]&chain=[chain]&to_address=[to_address]&token=[token]&amount=[amount]
```


## Pay to email in PUSDC

The tool allow to send `USDC` without knowing the receipt ETH address.
Pass the paramters with the authenticator OTP `code` to give the permission.

Parameters:

code: Authenticator code in 6 digits. It will be valided for 5 minutes, but can only be used for once.

chain: Current support `base` only.

token: Current support `USDC` only.

amount: In decimal like `1.2` USDC stand for 1200000 in int with 6 decemal places.

to_email: The email address we are sending to.


The on-chain call deposit fund with a `txNo` return in curl json
```bash
curl http://127.0.0.1:5333/pay2email?code=[code]&chain=[chain]&token=[token]&amount=[amount]&to_email=[to_email]
```

