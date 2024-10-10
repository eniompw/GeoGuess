from flask import Flask, render_template, request, jsonify
import requests
import random
import os
from dotenv import load_dotenv
import csv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Mapillary API configuration
base_url = "https://graph.mapillary.com/images"
access_token = os.getenv("MAPILLARY_ACCESS_TOKEN")
if not access_token:
    raise ValueError("MAPILLARY_ACCESS_TOKEN not set in environment variables")

# Load and cache capitals data
with open('capitals_sorted_by_gdp.csv', 'r') as f:
    csv_reader = csv.DictReader(f)
    capitals = list(csv_reader)

def generate_bbox(lat, lon, delta=0.001):
    """Generate a bounding box around given coordinates."""
    lat, lon = float(lat), float(lon)
    return f"{lon-delta:.4f},{lat-delta:.4f},{lon+delta:.4f},{lat+delta:.4f}"

def get_image_id(lat, lon, initial_delta=0.001, max_attempts=5):
    lat, lon = round(float(lat), 4), round(float(lon), 4)
    delta = initial_delta
    
    for attempt in range(max_attempts):
        bbox = generate_bbox(lat, lon, delta)
        params = {
            "access_token": access_token,
            "fields": "id",
            "bbox": bbox
        }
        request_url = f"{base_url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
        
        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            parsed_data = response.json()
            print(f"Attempt {attempt + 1}: Delta = {delta:.6f}")  # Print the current delta
            if parsed_data.get('data'):
                print(f"Image found with delta: {delta:.6f}")  # Print the delta when an image is found
                return parsed_data['data'][0]['id'], request_url
        except requests.RequestException as e:
            print(f"API request error: {str(e)}")
        
        # Increase delta exponentially
        delta *= 10
    
    print(f"No image found after {max_attempts} attempts. Final delta: {delta:.6f}")  # Print final delta if no image is found
    return None, request_url

@app.route('/')
def index():
    capital = random.choice(capitals)
    image_id, _ = get_image_id(capital['Latitude'], capital['Longitude'], initial_delta=0.001, max_attempts=5)
    if image_id:
        return render_template('index.html', image=image_id, city=capital['Capital'], country=capital['Country'])
    return "No image found. Please try again!"

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        lat = round(float(request.form['latitude']), 4)
        lon = round(float(request.form['longitude']), 4)
        image_id, request_url = get_image_id(lat, lon, initial_delta=0.001, max_attempts=5)
        
        if image_id:
            return jsonify({'image': image_id, 'lat': lat, 'lon': lon, 'request_url': request_url})
        return jsonify({'error': f"No image found for coordinates: {lat}, {lon}", 'request_url': request_url})
    
    return render_template('search.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
