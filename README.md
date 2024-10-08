# GeoGuessr Clone

This is a simple GeoGuessr-like web application that displays random street view images from world capitals using the Mapillary API. Users can test their geography knowledge by guessing the location of the displayed image.

## Project Structure

- `app.py`: Flask application that serves the images to the user.
- `capitals.csv`: Contains a list of 195 world capitals and their coordinates.
- `requirements.txt`: List of Python package dependencies.
- `templates/index.html`: Main HTML template for the web app, including the Mapillary viewer.
- `templates/404.html`: Custom 404 error page.
- `.env`: Configuration file for environment variables (not included in repository).

## Features

- Random selection of world capitals from a database of 195 locations.
- Street view images powered by Mapillary API.
- Interactive guessing system with immediate feedback.
- Custom 404 error page for improved user experience.
- Responsive design for various screen sizes.
- "New Location" button to quickly load a new challenge.

## How it works

1. The app selects a random capital from the `capitals.csv` file.
2. It generates a small bounding box around the capital's coordinates.
3. The app queries the Mapillary API to get an image within that bounding box.
4. The image is displayed to the user using the Mapillary.js viewer.
5. The user can input their guess for the location.
6. Feedback is provided on whether the guess is correct or not.
7. The correct location is revealed after the guess.

## Setup and Running

1. Ensure you have Python installed (Python 3.7+ recommended).
2. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/geoguessr-clone.git
   cd geoguessr-clone
   ```
3. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```
4. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
5. Create a `.env` file in the project root and add your Mapillary access token:
   ```bash
   MAPILLARY_ACCESS_TOKEN=your_access_token_here
   ```
6. Run the app:
   ```bash
   python app.py
   ```
7. Open your web browser and navigate to `http://localhost:5000`.

## Technical Details

- Flask web framework for the backend.
- Mapillary API for retrieving street view images.
- Mapillary.js for displaying interactive street view images.
- Python's `random` module for selecting random capitals.
- Environment variables for secure API key storage.
- Custom error handling for API requests and 404 errors.
- Responsive CSS for adaptable layout on different devices.

## Future Improvements

- Implement a scoring system to track user performance.
- Add a timer for each guess to increase challenge.
- Create difficulty levels based on country popularity or region.
- Develop a multiplayer mode for competitive play.
- Integrate a map view to show the correct location after guessing.
- Implement caching for capitals data to improve performance.
- Add user accounts and leaderboards.

## License

This project is open source and available under the [MIT License](LICENSE).

## Acknowledgments

- Mapillary for providing the street view imagery API.
- Flask community for the excellent web framework.
- Contributors to the `python-dotenv` package for simplified environment variable management.

## Note

This project uses a Mapillary access token. Ensure you keep your access token secure by using environment variables and not exposing it in public repositories.