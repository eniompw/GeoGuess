import requests
from urllib.parse import urlencode

api_base_url = "https://graph.mapillary.com/images"
mapillary_access_token = "API_KEY_HERE"

# Center point
lat, long = 51.5078, -0.1277

# Create bounding box (approximately 11m around the center point)
bbox_size = 0.0001
bbox = [
    round(long - bbox_size, 4),  # min longitude
    round(lat - bbox_size, 4),   # min latitude
    round(long + bbox_size, 4),  # max longitude
    round(lat + bbox_size, 4)    # max latitude
]

query_params = {
    "access_token": mapillary_access_token,
    "fields": "id",
    "bbox": ",".join(map(str, bbox))
}

# Construct and print the full request URL
encoded_params = urlencode(query_params, safe=",|")
full_url = f"{api_base_url}?{encoded_params}"
print("Request URL:")
print(full_url)

response = requests.get(api_base_url, params=query_params)
response_data = response.json()
first_image_id = response_data['data'][0]['id'] if response_data['data'] else None
print("\nResponse data:")
print(response_data)