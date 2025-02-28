# EIP-712 Signing with Fordefi

This repository contains a Python implementation for signing EIP-712 typed data using the Fordefi API. It demonstrates how to create, sign, and submit EIP-712 structured data for blockchain transactions.

## Overview

The script allows you to:
- Construct EIP-712 typed data messages
- Sign messages using Fordefi's secure vault infrastructure
- Submit signed transactions to the blockchain
- Decode and extract signature components (r, s, v)

## Prerequisites

- Python 3.6+
- Fordefi account with API access
- Environment variables configured with your Fordefi credentials

## Installation

1. Clone this repository
2. Install the required dependencies:

```bash
pip install requests python-dotenv
```

3. Create a `.env` file in the root directory with the following variables:

```
FORDEFI_API_USER_TOKEN=your_api_token
FORDEFI_EVM_VAULT_ID=your_vault_id
```

## Usage

Run the script with:

```bash
python signer/sign_eip712.py
```

## How It Works

1. The script loads your Fordefi credentials from environment variables
2. Constructs an EIP-712 typed data structure (in this example, a USDC token approval)
3. Creates a properly formatted request to the Fordefi API
4. Signs the request payload
5. Submits the transaction to Fordefi's API
6. Processes and displays the response, including the decoded signature components

## Example

The included example demonstrates signing a USDC token approval (Permit) on Ethereum mainnet. The typed data includes:
- Token contract details (USDC)
- Approval parameters (spender, amount, deadline)
- Chain ID and other required EIP-712 fields

## Project Structure

- `sign_eip712.py` - Main script for signing EIP-712 data
- `api_requests/push_to_api.py` - Handles API communication with Fordefi
- `request_builder/construct_request.py` - Builds properly formatted API requests
- `signing/signer.py` - Handles the signing process
