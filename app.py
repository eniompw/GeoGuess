from flask import Flask, render_template
import requests
import json
import random
import os
from dotenv import load_dotenv
from werkzeug.urls import quote  # Updated import

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Mapillary API configuration
base_url = "https://graph.mapillary.com/images"
access_token = os.getenv("MAPILLARY_ACCESS_TOKEN")

# Load and cache capitals data
def load_capitals():
    with open('capitals.csv', 'r') as f:
        return f.readlines()[1:]  # Skip header

capitals = load_capitals()

def generate_bbox(lat, lon, delta=0.002):
    """Generate a bounding box around given coordinates."""
    return f"{float(lat)-delta},{float(lon)-delta},{float(lat)+delta},{float(lon)+delta}"

@app.route('/')
def index():
    # Select a random capital
    capital = random.choice(capitals).strip().split(',')
    city, country, lat, lon = capital
    
    print(f"Debug: Selected city is {city}")

    # Generate bounding box
    bbox = generate_bbox(lat, lon)

    # Set up API request parameters
    params = {
        "access_token": access_token,
        "fields": "id",
        "bbox": bbox
    }

    try:
        # Make API request
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise an exception for bad responses
        parsed_data = response.json()

        print(f"Debug: API Response - {response.status_code}")
        print(f"Debug: Response content - {response.text[:200]}...")  # Print first 200 characters

        if parsed_data.get('data'):
            image_id = parsed_data['data'][0]['id']
            return render_template('index.html', image=image_id, city=city, country=country)
        else:
            print(f"Debug: No image found for {city}, {country}. bbox: {bbox}")
            return f"No image found for {city}, {country}. Please try again!"

    except requests.RequestException as e:
        print(f"Debug: Request Exception - {str(e)}")
        if hasattr(e.response, 'text'):
            print(f"Debug: Error response content - {e.response.text[:200]}...")
        return f"An error occurred: {str(e)}"

    except Exception as e:
        print(f"Debug: Unexpected error - {str(e)}")
        return f"An unexpected error occurred: {str(e)}"

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
