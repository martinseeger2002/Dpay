import json

# Load the original JSON data from 'OW.json'
with open('OW.json', 'r') as file:
    original_data = json.load(file)

# Transform the data to the new simpler format
transformed_data = []
for item in original_data:
    new_item = {
        "inscriptionId": item["id"],
        "name": item["meta"]["name"]
    }
    transformed_data.append(new_item)

# Save the transformed data to a new JSON file
with open('DM.json', 'w') as file:
    json.dump(transformed_data, file, indent=4)

print("The JSON data has been transformed and saved to 'simplified.json'.")
