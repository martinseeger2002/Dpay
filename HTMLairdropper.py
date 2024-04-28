import subprocess
import time
import json
import re
import os
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

# Environment variables are used to securely store sensitive data such as RPC credentials.
# These should be set in your operating system or through your deployment environment.
rpc_user = os.getenv('RPC_USER', 'your_default_rpc_username')
rpc_password = os.getenv('RPC_PASSWORD', 'your_default_rpc_password')
rpc_host = os.getenv('RPC_HOST', 'localhost')
rpc_port = os.getenv('RPC_PORT', '22555')  # Default Dogecoin RPC port

# Setting up the AuthServiceProxy client with the RPC server.
# This client is used to communicate with the Dogecoin node via JSON-RPC.
rpc_connection = AuthServiceProxy(f"http://{rpc_user}:{rpc_password}@{rpc_host}:{rpc_port}/")

def read_last_output(json_file_name):
    """
    Reads the last output JSON file to determine the number of entries already processed.
    This helps in resuming the process from the last successful point after a disruption.

    Args:
    json_file_name (str): The file name of the JSON where the output is stored.

    Returns:
    int: The number of entries that have been processed.
    """
    if os.path.exists(json_file_name):
        try:
            with open(json_file_name, 'r') as file:
                data = json.load(file)
                return len(data)  # Return the count of entries in the JSON file.
        except json.JSONDecodeError as e:
            print(f"JSON decode error in {json_file_name}: {e}")
    return 0  # If the file does not exist or is empty, return 0.

def extract_details(file_name):
    """
    Extracts all details from the provided JSON file which contains the list of addresses and other necessary data for minting.

    Args:
    file_name (str): The file name of the JSON containing the air drop list.

    Returns:
    list: A list of dictionaries each containing details from the air drop list.
    """
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            return json.load(file).get('airDropList', [])  # Extract the airDropList array from JSON.
    except Exception as e:
        print(f"An error occurred while reading {file_name}: {e}")
        return []

def update_json_file(image_path, txid, details):
    """
    Updates or creates a JSON file with minting details including transaction ID and associated address.

    Args:
    image_path (str): The path to the image file being inscribed.
    txid (str): The transaction ID of the minting process.
    details (dict): A dictionary containing details of the air drop, including the Dogecoin address.
    """
    json_file_name = "airDropOutput.json"
    try:
        data = {}
        if os.path.exists(json_file_name):
            with open(json_file_name, 'r') as file:
                data = json.load(file)
        key = os.path.basename(image_path)
        data[key] = {"txid": txid, "address": details['dogecoin_address']}
        with open(json_file_name, 'w') as file:
            json.dump(data, file, indent=4)  # Update or create the JSON file with new data.
    except Exception as e:
        print(f"Error updating {json_file_name}: {e}")

def process_mint_batch(start, end, directory, file_prefix, file_extension, details_list):
    """
    Processes a batch of minting commands for a range of image files and associated addresses.

    Args:
    start (int): The starting index for processing.
    end (int): The ending index for processing.
    directory (str): The directory where image files are stored.
    file_prefix (str): The prefix of the image file names.
    file_extension (str): The extension of the image files.
    details_list (list): A list of details including addresses for minting.

    Returns:
    str: The transaction ID of the last successful mint in the batch.
    """
    last_txid = ""
    for i in range(start, min(end, start + 12)):  # Limit the processing to 12 items at a time for safety.
        details = details_list[i - start]
        file_number = str(i).zfill(5)
        image_path = os.path.join(directory, f"{file_prefix}{file_number}.{file_extension}")
        if not os.path.exists(image_path):
            print(f"File not found: {image_path}")
            continue  # Skip to the next file if the current one does not exist.

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
    """
    Waits for a transaction to be confirmed by checking its status periodically until it has at least one confirmation.

    Args:
    txid (str): The transaction ID to check for confirmation.
    """
    while True:
        try:
            tx_info = rpc_connection.gettransaction(txid)
            if tx_info and tx_info.get("confirmations", 0) >= 1:
                print(f"Transaction {txid} is confirmed.")
                break
        except JSONRPCException as e:
            print(f"Error fetching transaction {txid}: {e}")
        time.sleep(10)  # Pause for 10 seconds between checks to avoid excessive querying.

def continuous_minting_process(directory, file_prefix, file_extension):
    """
    Continuously processes minting in batches until all items in the list are processed. It resumes from the last successfully processed item based on the output JSON file.

    Args:
    directory (str): The directory where the image files are stored.
    file_prefix (str): The prefix of the image file names.
    file_extension (str): The extension of the image files.
    """
    last_count = read_last_output('airDropOutput.json')  # Determine the last processed count from the output JSON.
    details_list = extract_details('airDropList.json')
    details_list = details_list[last_count:]  # Start processing from the next item after the last processed count.
    batch_size = 12
    num_batches = (len(details_list) + batch_size - 1) // batch_size  # Calculate the total number of batches.

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

# Initialize main variables and start process
directory = 'E:\\nodedoginals\\dogecoin-ordinals-drc-20-inscription\\stones'
file_prefix = 'dpaystone'
file_extension = 'html'

continuous_minting_process(directory, file_prefix, file_extension)
