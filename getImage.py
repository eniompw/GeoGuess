import requests

API_BASE_URL = "https://graph.mapillary.com"
ACCESS_TOKEN = "API_KEY_HERE"

def get_image_by_key(image_key):
    """Fetch and download an image from Mapillary API using its image key."""
    try:
        # Prepare API request
        url = f"{API_BASE_URL}/{image_key}"
        params = {"access_token": ACCESS_TOKEN, "fields": "thumb_2048_url"}
        
        # Get image URL from API
        response = requests.get(url, params=params)
        response.raise_for_status()
        image_url = response.json()["thumb_2048_url"]

        # Download image
        image_response = requests.get(image_url)
        image_response.raise_for_status()
        filename = f"{image_key}.jpg"
        
        with open(filename, 'wb') as f:
            f.write(image_response.content)

        print(f"Image downloaded successfully: {filename}")
        return filename

    except requests.RequestException as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    # Example usage
    result = get_image_by_key("550092599700936")
    print(f"Result: {'Success' if result else 'Failure'}")

# Example full request URL:
# https://graph.mapillary.com/550092599700936?access_token=MLY%7C8679192948798465%7C149d6f039d3a1b62556096a4875b32f6&fields=thumb_2048_url