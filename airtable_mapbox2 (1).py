import requests
import json

# Configuration
AIRTABLE_PERSONAL_ACCESS_TOKEN = 'pat2EF6C3VNhTOk3Q.18e95d9749e196f92b172b4805d896b016f5662359ae12f0140af55a8275a6fc'
BASE_ID = 'app8IbOvqx9URXwkJ'
TABLE_NAME = 'Main'
MAPBOX_ACCESS_TOKEN = 'pk.eyJ1IjoiaGVyb21hcCIsImEiOiJjbHg3c3BkYWwwcjNhMnFyMG5vYm9xNmxuIn0.wTTuJeSzadS8o4lMIhH_Jw'

# Function to fetch all records from Airtable with a filter
def fetch_airtable_records():
    url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_PERSONAL_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    params = {
        "filterByFormula": "AND({Category/Layers} = '100 Free Things To Do', {Address} != '')"
    }
    records = []
    offset = None

    while True:
        if offset:
            params['offset'] = offset

        response = requests.get(url, headers=headers, params=params)
        print("Response Status Code:", response.status_code)
        print("Response Content:", response.text)

        if response.status_code != 200:
            raise Exception(f"Error fetching records from Airtable: {response.status_code}, {response.text}")

        data = response.json()
        records.extend(data.get('records', []))

        offset = data.get('offset')
        if not offset:
            break

    return records

# Function to geocode address using MapBox API
def geocode_address(address):
    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{address}.json"
    params = {
        'access_token': MAPBOX_ACCESS_TOKEN,
        'limit': 1
    }
    response = requests.get(url, params=params)
    data = response.json()
    if data['features']:
        coordinates = data['features'][0]['geometry']['coordinates']
        return {
            'latitude': coordinates[1],
            'longitude': coordinates[0]
        }
    else:
        return None

# Process records and geocode addresses
def process_records(records):
    locations = []
    for record in records:
        fields = record['fields']
        address = fields.get("Address")
        if address:
            print(f"Geocoding address: {address}")
            coords = geocode_address(address)
            if coords:
                print(f"Coordinates for {address}: {coords}")
                location = {
                    "name": fields.get("Name"),
                    "description": fields.get("Description"),
                    "website": fields.get('Website Links'),
                    "email": fields.get('E-Mail Address'),
                    "phone": fields.get('Phone Number'),
                    "hours_of_Operation": fields.get('Hours of Operation'),
                    "latitude": coords['latitude'],
                    "longitude": coords['longitude']
                }
                locations.append(location)
            else:
                print(f"Failed to geocode address: {address}")
        else:
            print(f"No address found in record: {record}")
    return locations

# Fetch and process records
records = fetch_airtable_records()
if not records:
    print("No records fetched from Airtable.")
else:
    print(f"Fetched {len(records)} records from Airtable.")

locations = process_records(records)
if not locations:
    print("No locations processed.")
else:
    print(f"Processed {len(locations)} locations.")

# Save the locations data to a JSON file
with open('locations.json', 'w') as f:
    json.dump(locations, f)
