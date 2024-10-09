import requests

api_base_url = "https://graph.mapillary.com/images"
mapillary_access_token = "API_KEY_HERE"

# Center point
lat, long = 51.5078, -0.1277

# Create bounding box (approximately 11m around the center point)
bbox_size = 0.0001
bbox = [
    long - bbox_size,  # min longitude
    lat - bbox_size,   # min latitude
    long + bbox_size,  # max longitude
    lat + bbox_size    # max latitude
]

query_params = {
    "access_token": mapillary_access_token,
    "fields": "id",
    "bbox": ",".join(map(str, bbox))
}

response = requests.get(api_base_url, params=query_params)
response_data = response.json()
print(response_data)
first_image_id = response_data['data'][0]['id']