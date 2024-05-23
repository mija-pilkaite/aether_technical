import requests
from urllib.parse import quote_plus
import json

def get_utility_data(address):
    # Replace 'your_api_key' with the actual API key
    api_key = 'dxCkxOIHeeuHa0UbbHn43E3m735EFnxRRQpsyoUI'
    url = f'https://api.openei.org/services/rest/util_rates?version=3&api_key={api_key}&address={address}'
    response = requests.get(url)
    return response.json() if response.status_code == 200 else None




def get_lat_lon(address, api_key_maps):
    address = quote_plus(address)
    url = f'https://geocode.maps.co/search?q={address}&api_key={api_key_maps}'
    response = requests.get(url)
    if response.status_code == 200:
        try:
            data = response.json()
            lat = data[0]['lat']
            lon = data[0]['lon']
            return lat, lon
        except json.JSONDecodeError:
            print("Error decoding JSON response")
            print(response.text)  # Print the raw response text
            return None, None
    else:
        print(f"Error: Received status code {response.status_code}")
        print(response.text)  # Print the raw response text
        return None, None
