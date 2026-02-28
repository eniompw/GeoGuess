from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import requests
import random
import os
from dotenv import load_dotenv
import csv
import time
import logging

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

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

DIFFICULTY_RANGES = [(0, 40), (40, 80), (80, 120), (120, 160), (160, None)]
TOTAL_ROUNDS = len(DIFFICULTY_RANGES)
MAX_TRIES = 3


def get_image_id(lat, lon, initial_delta=0.001, max_attempts=5):
    lat, lon = round(float(lat), 4), round(float(lon), 4)
    delta = initial_delta

    for _ in range(max_attempts):
        bbox = f"{lon-delta:.4f},{lat-delta:.4f},{lon+delta:.4f},{lat+delta:.4f}"
        params = {
            "access_token": ACCESS_TOKEN,
            "fields": "id",
            "bbox": bbox,
            "limit": 10,
        }

        try:
            response = requests.get(BASE_URL, params=params)
            response.raise_for_status()
            data = response.json().get('data', [])
            if data:
                return random.choice(data)['id']
        except requests.RequestException as e:
            logger.error(f"API request error: {e}")

        delta *= 10

    return None


def get_city_for_round(current_round):
    start, end = DIFFICULTY_RANGES[current_round]
    capital = random.choice(CAPITALS[start:end])
    image_id = get_image_id(capital['Latitude'], capital['Longitude'])
    return capital, image_id


def fetch_image_with_retries(current_round):
    for attempt in range(MAX_TRIES):
        try:
            capital, image_id = get_city_for_round(current_round)
            if image_id:
                return capital, image_id
        except requests.RequestException as e:
            logger.error(f"API request error (attempt {attempt + 1}): {e}")
        time.sleep(1)
    return None, None


def format_location(capital):
    return f"{capital['Capital']}, {capital['Country']}"


def reset_session():
    session['current_round'] = 0
    session['correct_answers'] = 0
    session['incorrect_tries'] = 0


@app.route('/')
def index():
    reset_session()
    logger.info("New game started")
    return render_template('index.html', round=1, access_token=ACCESS_TOKEN)


@app.route('/get_image')
def get_image():
    current_round = session.get('current_round', 0)
    capital, image_id = fetch_image_with_retries(current_round)

    if not image_id:
        logger.error("Failed to fetch image after multiple attempts")
        return jsonify({'error': 'Unable to fetch image. Please try again.', 'fallback': True})

    session['current_capital'] = capital
    location_name = format_location(capital)
    logger.info(f"Image fetched for round {current_round + 1}: {location_name}")
    return jsonify({
        'image_id': image_id,
        'location_name': location_name,
        'round': current_round + 1,
    })


@app.route('/guess', methods=['POST'])
def guess():
    user_guess = request.form['guess'].lower().strip()
    current_capital = session.get('current_capital')

    if not current_capital:
        logger.error("No current capital in session")
        return jsonify({'error': 'No current capital in session'})

    logger.info(f"Guess received: {user_guess}")
    correct = user_guess in (current_capital['Capital'].lower(), current_capital['Country'].lower())

    if correct:
        session['correct_answers'] = session.get('correct_answers', 0) + 1
        session['current_round'] = session.get('current_round', 0) + 1
        session['incorrect_tries'] = 0
        return jsonify({
            'correct': True,
            'message': f"Correct! It was {format_location(current_capital)}.",
            'next_round': True,
        })

    incorrect_tries = session.get('incorrect_tries', 0) + 1
    session['incorrect_tries'] = incorrect_tries

    if incorrect_tries >= MAX_TRIES:
        current_round = session.get('current_round', 0)
        new_capital, new_image_id = get_city_for_round(current_round)
        session['current_capital'] = new_capital
        session['incorrect_tries'] = 0
        return jsonify({
            'correct': False,
            'message': f"Wrong! It was {format_location(current_capital)}. Let's try a new city!",
            'new_image': new_image_id,
            'new_location_name': format_location(new_capital),
            'tries_reset': True,
        })

    remaining = MAX_TRIES - incorrect_tries
    return jsonify({
        'correct': False,
        'message': f"Wrong! Try again. You have {remaining} {'try' if remaining == 1 else 'tries'} left.",
        'tries_left': remaining,
    })


@app.route('/next_round')
def next_round():
    current_round = session.get('current_round', 0)
    if current_round >= TOTAL_ROUNDS:
        return render_template('game_over.html', score=session.get('correct_answers', 0))
    return render_template('index.html', round=current_round + 1, access_token=ACCESS_TOKEN)


@app.route('/new_game')
def new_game():
    return redirect(url_for('index'))


@app.route('/map')
def map():
    return render_template('latlong.html')


@app.route('/latlong')
def latlong():
    lat = request.args.get('lat')
    long = request.args.get('long')
    logger.info(f"Lat/Long received: {lat}, {long}")
    return f"{lat} : {long}"


if __name__ == '__main__':
    app.run(debug=True)
