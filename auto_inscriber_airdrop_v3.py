import subprocess
import time
import json
import re
import os

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

def run_node_commands(start, end, directory, file_prefix, file_extension, details_list):
    for i, details in zip(range(start, end + 1), details_list):
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
            txid = txid_search.group(1)
            print("Successful mint, updating JSON file")
            update_json_file(image_path, txid, details)
        else:
            handle_errors(result_mint.stdout)

def handle_errors(output):
    if "'64: too-long-mempool-chain'" in output:
        print("Detected specific error message, proceeding to wallet sync...")
        while True:
            result_sync = subprocess.run("node . wallet sync", shell=True, capture_output=True, text=True)
            time.sleep(1)
            print("Output from wallet sync command:")
            print(result_sync.stdout)
            if "inscription txid" in result_sync.stdout:
                txid = re.search("inscription txid: (\\w+)", result_sync.stdout).group(1)
                update_json_file(image_path, txid, details)
                break
            elif "'64: too-long-mempool-chain'" in result_sync.stdout:
                print("Retrying in 240 seconds...")
                time.sleep(240)
            else:
                print("Unknown response, stopping the retry loop.")
                break

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
            "address": details['dogecoin_address'],
        }
        with open(json_file_name, 'w') as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print(f"Error updating {json_file_name}: {e}")

file_name = 'airDropList.json'
details_list = extract_details(file_name)
directory = 'E:\\nodedoginals\\dogecoin-ordinals-drc-20-inscription\\stones'
file_prefix = 'dpaystone'
file_extension = 'html'
start = 1
end = 70
run_node_commands(start, end, directory, file_prefix, file_extension, details_list)
