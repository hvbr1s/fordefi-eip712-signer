import os
import datetime
import base64
import json
import requests
from dotenv import load_dotenv
from api_requests.push_to_api import make_api_request
from request_builder.construct_request import construct_request
from signing.signer import sign
from eth_utils.curried import to_hex

load_dotenv()
FORDEFI_API_USER_TOKEN = os.getenv("FORDEFI_API_USER_TOKEN")
FORDEFI_EVM_VAULT_ID = os.getenv("FORDEFI_EVM_VAULT_ID")
PATH = "/api/v1/transactions/create-and-wait"

typed_data = {
    "types": {
        "EIP712Domain": [{
            "name": "name",
            "type": "string"
        }, {
            "name": "version",
            "type": "string"
        }, {
            "name": "chainId",
            "type": "uint256"
        }, {
            "name": "verifyingContract",
            "type": "address"
        }],
        "Permit": [{
            "name": "owner",
            "type": "address"
        }, {
            "name": "spender",
            "type": "address"
        }, {
            "name": "value",
            "type": "uint256"
        }, {
            "name": "nonce",
            "type": "uint256"
        }, {
            "name": "deadline",
            "type": "uint256"
        }]
    },
    "primaryType": "Permit",
    "domain": {
        "name": "USD Coin",
        "verifyingContract": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
        "chainId": 1,
        "version": "2"
    },
    "message": {
        "deadline": 1767166198,
        "nonce": 1000,
        "spender": "0x1111111254fb6c44bac0bed2854e76f90643097d",
        "owner": "0x8BFCF9e2764BC84DE4BBd0a0f5AAF19F47027A73",
        "value": "115792089237316195423570985008687907853269984665640564039457584007913129639935"
    }
}

def main():

    if not FORDEFI_API_USER_TOKEN:
        print("Error: FORDEFI_API_TOKEN environment variable is not set")
        return
    
    typed_message = json.dumps(typed_data)
    hex_encoded_message = to_hex(text=typed_message)
    print(f"Hex encoded message: {hex_encoded_message}")
    
    request_json = construct_request(FORDEFI_EVM_VAULT_ID, typed_message)

    request_body = json.dumps(request_json)
    print(request_body)
    timestamp = datetime.datetime.now().strftime("%s")
    payload = f"{PATH}|{timestamp}|{request_body}"
        
    signature = sign(payload=payload)

    try: 
        method = "post"   
        print("Making API request to Fordefi 📡")
        resp_tx = make_api_request(PATH, FORDEFI_API_USER_TOKEN, signature, timestamp, request_body, method=method)
        try:
            print("\nResponse Data:")
            response_data = resp_tx.json()
            print(json.dumps(response_data, indent=2))

            # OPTIONAL Decode signature
            signature_b64 = response_data.get("signatures")[0]
            print(f"Signature -> {signature_b64}")
            signature = base64.b64decode(signature_b64)
            # Extract r, s, v components
            r = int.from_bytes(signature[0:32], byteorder='big')
            s = int.from_bytes(signature[32:64], byteorder='big')       
            # For v, use the chain_id from your typed data
            chain_id = typed_data["domain"]["chainId"]
            v = int(signature[-1]) + 35 + 2 * chain_id
            
            print(f"r: {hex(r)}")
            print(f"s: {hex(s)}")
            print(f"v: {v}")

        except json.JSONDecodeError:
            print("Failed printing response data!")
        
        resp_tx.raise_for_status()
        return resp_tx
    except requests.exceptions.HTTPError as e:
        error_message = f"HTTP error occurred: {str(e)}"
        if resp_tx.text:
            try:
                error_detail = resp_tx.json()
                error_message += f"\nError details: {error_detail}"
            except json.JSONDecodeError:
                error_message += f"\nRaw response: {resp_tx.text}"
        raise RuntimeError(error_message)
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Network error occurred: {str(e)}")

    except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()