import requests

# API configuration
API_BASE_URL = "https://graph.mapillary.com/images"
ACCESS_TOKEN = "API_KEY_HERE"

# Center point and bounding box
lat, lon = 51.5078, -0.1277
bbox_size = 0.0001
bbox = f"{lon-bbox_size},{lat-bbox_size},{lon+bbox_size},{lat+bbox_size}"

# Query parameters
params = {
    "access_token": ACCESS_TOKEN,
    "fields": "id",
    "bbox": bbox
}

# Make API request
response = requests.get(API_BASE_URL, params=params)
data = response.json()

# Print request URL and response data
print(f"Request URL:\n{response.url}\n")
print(f"Response data:\n{data}")

# Extract first image ID if available
first_image_id = data['data'][0]['id'] if data.get('data') else None
print(f"\nFirst image ID: {first_image_id}")