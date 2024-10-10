from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import requests
import random
import os
from dotenv import load_dotenv
import csv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Mapillary API configuration
BASE_URL = "https://graph.mapillary.com/images"
ACCESS_TOKEN = os.getenv("MAPILLARY_ACCESS_TOKEN")
if not ACCESS_TOKEN:
    raise ValueError("MAPILLARY_ACCESS_TOKEN not set in environment variables")

# Load and cache capitals data
with open('capitals_sorted_by_gdp.csv', 'r') as f:
    CAPITALS = list(csv.DictReader(f))

# Define difficulty ranges
DIFFICULTY_RANGES = [(0, 40), (40, 80), (80, 120), (120, 160), (160, None)]

def get_image_id(lat, lon, initial_delta=0.001, max_attempts=5):
    lat, lon = round(float(lat), 4), round(float(lon), 4)
    delta = initial_delta
    
    for attempt in range(max_attempts):
        bbox = f"{lon-delta:.4f},{lat-delta:.4f},{lon+delta:.4f},{lat+delta:.4f}"
        params = {
            "access_token": ACCESS_TOKEN,
            "fields": "id",
            "bbox": bbox
        }
        
        try:
            response = requests.get(BASE_URL, params=params)
            response.raise_for_status()
            data = response.json().get('data', [])
            if data:
                return random.choice(data)['id']
        except requests.RequestException as e:
            print(f"API request error: {str(e)}")
        
        delta *= 10
    
    return None

def get_city_for_round(current_round):
    start, end = DIFFICULTY_RANGES[current_round]
    capital = random.choice(CAPITALS[start:end if end else None])
    image_id = get_image_id(capital['Latitude'], capital['Longitude'])
    return capital, image_id

def start_new_round():
    current_round = session.get('current_round', 0)
    
    if current_round >= len(DIFFICULTY_RANGES):
        return render_template('game_over.html', score=session.get('correct_answers', 0))
    
    capital, image_id = get_city_for_round(current_round)
    
    if image_id:
        session['current_capital'] = capital
        location_name = f"{capital['Capital']}, {capital['Country']}"
        return render_template('index.html', image=image_id, round=current_round + 1, location_name=location_name)
    return "No image found. Please try again!"

@app.route('/')
def index():
    session['current_round'] = 0
    session['correct_answers'] = 0
    session['incorrect_tries'] = 0
    return start_new_round()

@app.route('/guess', methods=['POST'])
def guess():
    user_guess = request.form['guess'].lower().strip()
    current_capital = session.get('current_capital')
    current_round = session.get('current_round', 0)
    incorrect_tries = session.get('incorrect_tries', 0)
    
    if current_capital:
        correct_capital = current_capital['Capital'].lower()
        correct_country = current_capital['Country'].lower()
        
        if user_guess == correct_capital or user_guess == correct_country:
            session['correct_answers'] = session.get('correct_answers', 0) + 1
            session['current_round'] = current_round + 1
            session['incorrect_tries'] = 0
            return jsonify({
                'correct': True,
                'message': f"Correct! It was {current_capital['Capital']}, {current_capital['Country']}.",
                'next_round': True
            })
        else:
            incorrect_tries += 1
            session['incorrect_tries'] = incorrect_tries
            
            if incorrect_tries >= 3:
                new_capital, new_image_id = get_city_for_round(current_round)
                session['current_capital'] = new_capital
                session['incorrect_tries'] = 0
                return jsonify({
                    'correct': False,
                    'message': f"Wrong! It was {current_capital['Capital']}, {current_capital['Country']}. Let's try a new city!",
                    'new_image': new_image_id,
                    'new_location_name': f"{new_capital['Capital']}, {new_capital['Country']}",
                    'tries_reset': True
                })
            else:
                return jsonify({
                    'correct': False,
                    'message': f"Wrong! Try again. You have {3 - incorrect_tries} {'try' if 3 - incorrect_tries == 1 else 'tries'} left.",
                    'tries_left': 3 - incorrect_tries
                })
    else:
        return jsonify({'error': 'No current capital in session'})

@app.route('/next_round')
def next_round():
    return start_new_round()

@app.route('/new_game')
def new_game():
    session['current_round'] = 0
    session['correct_answers'] = 0
    session['incorrect_tries'] = 0
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)