import json

# Load the JSON data from the file
with open('addresses.json', 'r') as file:
    data = json.load(file)

# Extract the Dogecoin addresses
addresses = [entry['dogecoin_address'] for entry in data['airDropList']]

# Save the addresses to a new text file in the desired format
with open('addresses.txt', 'w') as file:
    json.dump(addresses, file, indent=4)

print("Addresses have been successfully written to addresses.txt")
