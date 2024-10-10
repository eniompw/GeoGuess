from flask import Flask, render_template, request, jsonify, session
import requests
import random
import os
from dotenv import load_dotenv
import csv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Set a secret key for session management

# Mapillary API configuration
base_url = "https://graph.mapillary.com/images"
access_token = os.getenv("MAPILLARY_ACCESS_TOKEN")
if not access_token:
    raise ValueError("MAPILLARY_ACCESS_TOKEN not set in environment variables")

# Load and cache capitals data
with open('capitals_sorted_by_gdp.csv', 'r') as f:
    csv_reader = csv.DictReader(f)
    capitals = list(csv_reader)

# Define difficulty levels
DIFFICULTY_RANGES = [
    (0, 40),    # Top 40 capitals
    (40, 80),   # Next 40 capitals
    (80, 120),  # Next 40 capitals
    (120, 160), # Next 40 capitals
    (160, None) # Remaining capitals
]

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
    # Initialize or reset the game session
    session['current_round'] = 0
    session['correct_answers'] = 0
    return start_new_round()

def start_new_round():
    current_round = session.get('current_round', 0)
    
    if current_round >= len(DIFFICULTY_RANGES):
        return render_template('game_over.html', score=session.get('correct_answers', 0))
    
    start, end = DIFFICULTY_RANGES[current_round]
    capital = random.choice(capitals[start:end if end else None])
    
    # Debugging: Print the selected capital and its position
    capital_index = capitals.index(capital)
    print(f"Selected capital: {capital['Capital']}, {capital['Country']}")
    print(f"Position in list: {capital_index + 1} out of {len(capitals)}")
    print(f"Current difficulty range: {start} - {end}")
    
    image_id, _ = get_image_id(capital['Latitude'], capital['Longitude'], initial_delta=0.001, max_attempts=5)
    if image_id:
        session['current_capital'] = capital
        # Pass both capital and country to the template
        location_name = f"{capital['Capital']}, {capital['Country']}"
        return render_template('index.html', image=image_id, round=current_round + 1, location_name=location_name)
    return "No image found. Please try again!"

@app.route('/guess', methods=['POST'])
def guess():
    user_guess = request.form['guess'].lower()
    current_capital = session.get('current_capital')
    
    if current_capital and user_guess == current_capital['Capital'].lower():
        session['correct_answers'] = session.get('correct_answers', 0) + 1
        session['current_round'] = session.get('current_round', 0) + 1
        return jsonify({
            'correct': True,
            'message': f"Correct! It was {current_capital['Capital']}, {current_capital['Country']}.",
            'capital': current_capital['Capital'],
            'country': current_capital['Country'],
            'latitude': current_capital['Latitude'],
            'longitude': current_capital['Longitude']
        })
    elif current_capital:
        return jsonify({
            'correct': False,
            'message': f"Wrong! It was {current_capital['Capital']}, {current_capital['Country']}.",
            'capital': current_capital['Capital'],
            'country': current_capital['Country'],
            'latitude': current_capital['Latitude'],
            'longitude': current_capital['Longitude']
        })
    else:
        return jsonify({'error': 'No current capital in session'})

@app.route('/next_round')
def next_round():
    return start_new_round()

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
