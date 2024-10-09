from flask import Flask, render_template, request, jsonify
import requests
import random
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Mapillary API configuration
base_url = "https://graph.mapillary.com/images"
access_token = os.getenv("MAPILLARY_ACCESS_TOKEN")

# Load and cache capitals data
with open('capitals.csv', 'r') as f:
    capitals = f.readlines()[1:]  # Skip header

def generate_bbox(lat, lon, delta=0.02):
    """Generate a bounding box around given coordinates."""
    lat, lon = float(lat), float(lon)
    return f"{lat-delta:.4f},{lon-delta:.4f},{lat+delta:.4f},{lon+delta:.4f}"

def get_image_id(lat, lon):
    # Round lat and lon to 4 decimal places
    lat = round(float(lat), 4)
    lon = round(float(lon), 4)
    
    bbox = generate_bbox(lat, lon)
    params = {
        "access_token": access_token,
        "fields": "id",
        "bbox": bbox
    }
    # Debug print statements
    print(f"Debug: Coordinates: {lat}, {lon}")
    print(f"Debug: Bounding box: {bbox}")
    request_url = f"{base_url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
    print(f"Debug: Request URL: {request_url}")
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        parsed_data = response.json()
        if parsed_data.get('data'):
            return parsed_data['data'][0]['id'], request_url
    except requests.RequestException as e:
        print(f"API request error: {str(e)}")
    return None, request_url

@app.route('/')
def index():
    city, country, lat, lon = random.choice(capitals).strip().split(',')
    image_id = get_image_id(lat, lon)
    if image_id:
        return render_template('index.html', image=image_id, city=city, country=country)
    return "No image found. Please try again!"

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        lat = round(float(request.form['latitude']), 4)
        lon = round(float(request.form['longitude']), 4)
        image_id, request_url = get_image_id(lat, lon)
        if image_id:
            return jsonify({'image': image_id, 'lat': lat, 'lon': lon, 'request_url': request_url})
        return jsonify({'error': f"No image found for coordinates: {lat}, {lon}", 'request_url': request_url})
    return render_template('search.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
