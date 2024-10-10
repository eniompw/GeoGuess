# GeoGuess Challenge

A web application that tests users' geography knowledge using street view images from world capitals.

## Features

- Random selection from 195 world capitals
- Search functionality for specific locations
- Interactive street view images via Mapillary API
- Progressive difficulty: 5 rounds based on GDP rankings
- Three attempts per location guess

## Project Structure

- `app.py`: Main Flask application
- `capitals_sorted_by_gdp.csv`: World capitals data
- `templates/`: HTML templates
- `vercel.json`: Vercel deployment configuration

## Setup and Running

1. Clone the repository and navigate to the project directory
2. Create and activate a virtual environment
3. Install dependencies: `pip install -r requirements.txt`
4. Set up `.env` file with your Mapillary access token
5. Run the app: `python app.py`
6. Open `http://localhost:5000` in your browser

## How it Works

1. App selects a random capital and fetches its street view image
2. User gets three attempts to guess the location
3. Correct guess advances to next round; all attempts used loads a new location

## Deployment

Use the included `vercel.json` for easy deployment on Vercel:

1. Sign up for Vercel and install Vercel CLI
2. Run `vercel` in the project directory
3. Follow the prompts to deploy

Remember to set up environment variables in the Vercel dashboard.

## License

This project is open source under the [MIT License](LICENSE).

## Acknowledgments

- Mapillary for the street view imagery API
- Flask community for the web framework