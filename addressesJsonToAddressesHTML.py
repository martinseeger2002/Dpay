import json

# Load the JSON data from the file
with open('addresses.json', 'r') as file:
    data = json.load(file)

# Extract the Dogecoin addresses and wrap them with <li> tags
addresses = [f"<li>{entry['dogecoin_address']}</li>" for entry in data['airDropList']]

# Save the addresses to a new text file with each address on a new line
with open('addresses.html', 'w') as file:
    for address in addresses:
        file.write(address + "\n")

print("Addresses have been successfully written to addresses.html")

