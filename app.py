from flask import Flask, render_template
import requests
import json

app = Flask(__name__)
base_url = "https://graph.mapillary.com/images"
access_token = "API_KEY_HERE"
bbox = "6.1475,46.2078,6.1477,46.2080"
params = {
    "access_token": access_token,
    "fields": "id",
    "bbox": bbox
}

@app.route('/')
def login():
    x = requests.get(base_url, params=params)
    parsed_data = json.loads(x.text)
    image = parsed_data['data'][0]['id']
    return render_template('jinja.html', image=image)
