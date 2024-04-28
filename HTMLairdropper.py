import subprocess
import time
import json
import re
import os
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

# Configuration for RPC connection
rpc_user = 'your_rpc_username'
rpc_password = 'your_rpc_password'
rpc_host = 'localhost'
rpc_port = '22555'  # Default Dogecoin RPC port
rpc_connection = AuthServiceProxy(f"http://{rpc_user}:{rpc_password}@{rpc_host}:{rpc_port}/")

def extract_details(file_name):
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return [{
            'dogecoin_address': entry['dogecoin_address']
        } for entry in data['airDropList']]
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def update_json_file(image_path, txid, details):
    json_file_name = "airDropOutput.json"
    data = {}
    try:
        if os.path.exists(json_file_name):
            with open(json_file_name, 'r') as file:
                data = json.load(file)
        key = os.path.basename(image_path)
        data[key] = {
            "txid": txid,
            "address": details['dogecoin_address']
        }
        with open(json_file_name, 'w') as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print(f"Error updating {json_file_name}: {e}")

def process_mint_batch(start, end, directory, file_prefix, file_extension, details_list):
    last_txid = ""
    for i in range(start, min(end, start + 12)):  # Ensure we only process up to 12 at a time
        details = details_list[i - start]  # Adjusted index since lists are 0-indexed
        file_number = str(i).zfill(5)
        image_path = os.path.join(directory, f"{file_prefix}{file_number}.{file_extension}")
        if not os.path.exists(image_path):
            print(f"File not found: {image_path}")
            continue

        mint_command = f"node . mint {details['dogecoin_address']} {image_path}"
        result_mint = subprocess.run(mint_command, shell=True, capture_output=True, text=True)
        print("Output from mint command:")
        print(result_mint.stdout)
        if result_mint.stderr:
            print("Error in mint command:")
            print(result_mint.stderr)

        txid_search = re.search("inscription txid: (\\w+)", result_mint.stdout)
        if txid_search:
            last_txid = txid_search.group(1)
            print(f"Successful mint, TXID: {last_txid}")
            update_json_file(image_path, last_txid, details)

    return last_txid

def wait_for_tx_confirmation(txid):
    while True:
        try:
            tx_info = rpc_connection.gettransaction(txid)
            if tx_info and tx_info.get("confirmations", 0) >= 1:
                print(f"Transaction {txid} is confirmed.")
                break
        except JSONRPCException as e:
            print(f"Error fetching transaction {txid}: {e}")
        time.sleep(10)  # Wait for 10 seconds before retrying

def continuous_minting_process(directory, file_prefix, file_extension, details_list):
    batch_size = 12
    num_batches = (len(details_list) + batch_size - 1) // batch_size  # Calculate total number of batches

    for batch_index in range(num_batches):
        start_index = batch_index * batch_size
        end_index = start_index + batch_size
        print(f"Processing batch from {start_index + 1} to {end_index}")

        last_txid = process_mint_batch(start_index + 1, end_index, directory, file_prefix, file_extension, details_list)
        if last_txid:
            print(f"Waiting for confirmation of TXID: {last_txid}")
            wait_for_tx_confirmation(last_txid)
        else:
            print("No valid transactions in this batch to wait for.")

# Main execution
file_name = 'airDropList.json'
details_list = extract_details(file_name)
directory = 'E:\\nodedoginals\\dogecoin-ordinals-drc-20-inscription\\stones'
file_prefix = 'dpaystone'
file_extension = 'html'

continuous_minting_process(directory, file_prefix, file_extension, details_list)
