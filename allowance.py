import os
import datetime
import json
import requests
from web3 import Web3
from dotenv import load_dotenv
from signing.signer import sign
from api_requests.push_to_api import make_api_request
from request_builder.construct_request import construct_allowance_request

load_dotenv()
FORDEFI_API_USER_TOKEN = os.getenv("FORDEFI_API_USER_TOKEN")
FORDEFI_EVM_VAULT_ID = os.getenv("FORDEFI_EVM_VAULT_ID")
FORDEFI_EVM_VAULT_ADDRESS = os.getenv("FORDEFI_EVM_VAULT_ADDRESS")
BASESCAN_API_KEY = os.getenv("BASESCAN_API_KEY") 
PATH = "/api/v1/transactions"

approval_config = {
    "dapp_contract_address": "0x111111125421cA6dc452d289314280a0f8842A65", # 1inch on Base
    "proxy_token_contract_address": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913", # USDC on Base (proxy)
    "impl_token_contract_address": "0x2Ce6311ddAE708829bc0784C967b7d77D19FD779", # USDC on Base (implementation contract)
    "evm_chain": "base",
    "allowance": 115792089237316195423570985008687907853269984665640564039457584007913129639935 # Unlimited allowance
}

def main():

    """Main function to execute an unlimited approval for 1inch on Base with Fordefi"""

    w3 = Web3(Web3.HTTPProvider("https://base-rpc.publicnode.com"))
    contract_address = approval_config["impl_token_contract_address"]

    # Fetch contract ABI from Basescan
    print(f"Fetching ABI for contract: {contract_address}")
    basescan_url = f"https://api.basescan.org/api?module=contract&action=getabi&address={contract_address}&apikey={BASESCAN_API_KEY}"
    response = requests.get(basescan_url)
    response_json = response.json()
    
    if response_json["status"] == "1" and response_json["message"] == "OK":
        contract_abi = response_json["result"]
    else:
        raise RuntimeError(f"Failed to fetch ABI: {response_json['message']}")

    # Create call data
    contract = w3.eth.contract(address=contract_address, abi=contract_abi)
    call_data = contract.functions.approve(
        approval_config["dapp_contract_address"], 
        approval_config["allowance"]
    ).build_transaction({
        'from': FORDEFI_EVM_VAULT_ADDRESS,
        'gas': 100000, # gas limit
        'gasPrice': w3.eth.gas_price,
        'nonce': 0  # This will be ignored by Fordefi API but needed for encoding
    })["data"]
    print("Encoded call data:", call_data)

    # Built API payload for Fordefi   
    request_json = construct_allowance_request(FORDEFI_EVM_VAULT_ID, approval_config["evm_chain"], approval_config["proxy_token_contract_address"], call_data)

    request_body = json.dumps(request_json)

    timestamp = datetime.datetime.now().strftime("%s")
    payload = f"{PATH}|{timestamp}|{request_body}"
        
    signature = sign(payload=payload)

    try: 
  
        print("Making API request to Fordefi 📡")
        method = "post" 
        resp_tx = make_api_request(PATH, FORDEFI_API_USER_TOKEN, signature, timestamp, request_body, method=method)

        try:

            response_data = resp_tx.json()
            # print("\nDEBUG - Response Data:")
            # print(json.dumps(response_data, indent=2))

        except json.JSONDecodeError:
            print("Failed printing response data!")
        
        resp_tx.raise_for_status()
        return resp_tx
    
    except requests.exceptions.HTTPError as e:
        error_message = f"HTTP error occurred: {str(e)}"
        if 'resp_tx' in locals() and resp_tx.text:
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
        raise

if __name__ == "__main__":
    main()