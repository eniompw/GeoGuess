# GeoGuessr Clone

This is a simple GeoGuessr-like web application that displays random street view images from world capitals using the Mapillary API.

## Project Structure

- `capitals.csv`: Contains a list of 195 world capitals and their coordinates.
- `app.py`: Flask application that serves the images to the user.
- `templates/index.html`: HTML template for the web app, including the Mapillary viewer.

## How it works

1. The app selects a random capital from the `capitals.csv` file.
2. It generates a small bounding box around the capital's coordinates.
3. The app queries the Mapillary API to get an image within that bounding box.
4. The image is displayed to the user using the Mapillary.js viewer.
5. The user can guess the location and then see the correct answer.

## Setup and Running

1. Make sure you have Python and Flask installed.
2. Clone this repository.
3. Install the required packages:
   ```bash
   pip install flask requests python-dotenv
   ```
4. Create a `.env` file in the project root and add your Mapillary access token:
   ```bash
   MAPILLARY_ACCESS_TOKEN=your_access_token_here
   ```
5. Run the app:
   ```bash
   python app.py
   ```
6. Navigate to `http://localhost:5000` in your browser.

## Technical Details

- The bounding box for the Mapillary API query uses 4 decimal places, giving approximately 15m resolution.
- The bounding box is generated with a delta of 0.002 around the capital's coordinates.
- The app uses Jinja2 templating to pass the Mapillary image ID, city, and country to the HTML.
- Mapillary.js is used to display the street view image.
- The application includes error handling for API requests and uses environment variables for sensitive information.

## Features

- Random selection of world capitals
- Street view images from Mapillary
- Display of city and country names after guessing
- "New Location" button to load a new random capital

## Note

This project uses a Mapillary access token. Make sure to keep your access token secure by using environment variables and not exposing it in public repositories.

## Additional Improvement Ideas

- Implement caching for capitals data in `app.py`
- Add a custom 404 error handler
- Create a form in `index.html` for users to submit their guesses
- Add a map view to show the correct location after guessing

## Future Improvements

- Add a scoring system
- Implement a timer for each guess
- Create a multiplayer mode
- Add difficulty levels based on country popularity or region