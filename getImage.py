import requests

API_BASE_URL = "https://graph.mapillary.com"
ACCESS_TOKEN = "API_KEY_HERE"

def get_image_by_key(image_key):
    try:
        # Get image URL
        params = {"access_token": ACCESS_TOKEN, "fields": "thumb_2048_url"}
        response = requests.get(f"{API_BASE_URL}/{image_key}", params=params)
        response.raise_for_status()
        image_url = response.json()["thumb_2048_url"]

        # Download image
        image_response = requests.get(image_url)
        image_response.raise_for_status()

        # Save image
        filename = f"{image_key}.jpg"
        with open(filename, 'wb') as f:
            f.write(image_response.content)

        print(f"Image downloaded successfully: {filename}")
        return filename

    except (requests.RequestException, KeyError) as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    image_key = "550092599700936"
    result = get_image_by_key(image_key)
    print(f"Result: {'Success' if result else 'Failure'}")