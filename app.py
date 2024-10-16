from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import requests
import random
import os
from dotenv import load_dotenv
import csv
import time
import logging
from datetime import datetime, timedelta, timezone

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.permanent_session_lifetime = timedelta(minutes=30)  # Set session timeout to 30 minutes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    
    max_attempts = 3
    
    for attempt in range(max_attempts):
        try:
            capital, image_id = get_city_for_round(current_round)
            
            if image_id:
                session['current_capital'] = capital
                location_name = f"{capital['Capital']}, {capital['Country']}"
                return render_template('index.html', image=image_id, round=current_round + 1, location_name=location_name)
            
        except requests.RequestException as e:
            print(f"API request error (attempt {attempt + 1}): {str(e)}")
        
        time.sleep(1)  # Wait for 1 second before retrying
    
    # If all attempts fail, return an error page
    return render_template('error.html', message="Unable to load the next round. Please try again.")

def check_session():
    if 'last_activity' not in session:
        session['last_activity'] = datetime.now(timezone.utc)
    elif datetime.now(timezone.utc) - session['last_activity'] > app.permanent_session_lifetime:
        logger.info("Session expired")
        return False
    session['last_activity'] = datetime.now(timezone.utc)
    return True

@app.before_request
def before_request():
    session.permanent = True
    if not check_session():
        return jsonify({'error': 'Session expired', 'redirect': url_for('index')})

@app.route('/')
def index():
    session['current_round'] = 0
    session['correct_answers'] = 0
    session['incorrect_tries'] = 0
    logger.info("New game started")
    return render_template('index.html', round=1)

@app.route('/get_image')
def get_image():
    if not check_session():
        return jsonify({'error': 'Session expired', 'redirect': url_for('index')})

    current_round = session.get('current_round', 0)
    max_attempts = 3
    
    for attempt in range(max_attempts):
        try:
            capital, image_id = get_city_for_round(current_round)
            
            if image_id:
                session['current_capital'] = capital
                location_name = f"{capital['Capital']}, {capital['Country']}"
                logger.info(f"Image fetched for round {current_round + 1}: {location_name}")
                return jsonify({
                    'image_id': image_id,
                    'location_name': location_name,
                    'round': current_round + 1
                })
            
        except requests.RequestException as e:
            logger.error(f"API request error (attempt {attempt + 1}): {str(e)}")
        
        time.sleep(1)  # Wait for 1 second before retrying
    
    logger.error("Failed to fetch image after multiple attempts")
    return jsonify({
        'error': 'Unable to fetch image. Please try again.',
        'fallback': True
    })

@app.route('/guess', methods=['POST'])
def guess():
    if not check_session():
        return jsonify({'error': 'Session expired', 'redirect': url_for('index')})

    user_guess = request.form['guess'].lower().strip()
    current_capital = session.get('current_capital')
    current_round = session.get('current_round', 0)
    incorrect_tries = session.get('incorrect_tries', 0)
    
    logger.info(f"Guess received: {user_guess}")
    
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
        logger.error("No current capital in session")
        return jsonify({'error': 'No current capital in session'})

@app.route('/next_round')
def next_round():
    if not check_session():
        return jsonify({'error': 'Session expired', 'redirect': url_for('index')})
    return start_new_round()

@app.route('/new_game')
def new_game():
    session['current_round'] = 0
    session['correct_answers'] = 0
    session['incorrect_tries'] = 0
    logger.info("New game started")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
