def construct_request(vault_id, data):
    
    print(f'Preparing transaction from Vault {vault_id}')

    request_json = {
     "signer_type": "api_signer",
     "sign_mode": "auto",
     "type": "evm_message",
     "details": {
         "type": "typed_message_type",
         "raw_data": data,
         "chain": "ethereum_mainnet"
     },
     "vault_id": vault_id,
     "note": "Typed Data message, permit 1inch to spend USDC",
     "timeout": 15,
     "wait_for_state": "signed"
     }

    return request_json

def construct_allowance_request(vault_id, evm_chain, proxy_token_contract_address, call_data):

    request_json = {

        "vault_id": vault_id,
        "signer_type": "api_signer",
        "type": "evm_transaction",
        "details": {
            "type": "evm_raw_transaction",
            "chain": f"{evm_chain}_mainnet",
            "gas": {
                "type": "priority",
                "priority_level": "medium"
            },
            "to": proxy_token_contract_address,
            "value": "0",
            "data": {
                "type": "hex",
                "hex_data": call_data
            }
          }
    }
    return request_json