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

def generate_bbox(lat, lon, delta=0.005):
    """Generate a bounding box around given coordinates."""
    return f"{float(lat)-delta},{float(lon)-delta},{float(lat)+delta},{float(lon)+delta}"

def get_image_id(lat, lon):
    bbox = generate_bbox(lat, lon)
    params = {
        "access_token": access_token,
        "fields": "id",
        "bbox": bbox
    }
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        parsed_data = response.json()
        if parsed_data.get('data'):
            return parsed_data['data'][0]['id']
    except requests.RequestException as e:
        print(f"API request error: {str(e)}")
    return None

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
        lat = request.form['latitude']
        lon = request.form['longitude']
        image_id = get_image_id(lat, lon)
        if image_id:
            return jsonify({'image': image_id, 'lat': lat, 'lon': lon})
        return jsonify({'error': f"No image found for coordinates: {lat}, {lon}"})
    return render_template('search.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
