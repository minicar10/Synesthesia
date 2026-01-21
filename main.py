"""
Entry point for the Synesthesia Spotify-Wyze integration.
Coordinates Spotify polling and Wyze lighting control.
"""
import os
import requests
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from PIL import Image
import numpy as np
from sklearn.cluster import KMeans
import time
import pygetwindow as gw
import mss

# Spotify API credentials
SPOTIPY_CLIENT_ID = '[your spotify client id]'
SPOTIPY_CLIENT_SECRET = '[your spotify client secret]'
SPOTIPY_REDIRECT_URI = '[your spotify redirect uri]'

# Wyze credentials and initial access token
WYZE_REFRESH_TOKEN = '[your refresh token]'
WYZE_ACCESS_TOKEN = '[your access token]'

# Spotify authorization
scope = "user-read-playback-state"

sp = Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                       client_secret=SPOTIPY_CLIENT_SECRET,
                                       redirect_uri=SPOTIPY_REDIRECT_URI,
                                       scope=scope))

# Function to refresh the Wyze access token
def refresh_wyze_token():
    global WYZE_ACCESS_TOKEN, WYZE_REFRESH_TOKEN
    refresh_token_url = "https://api.wyzecam.com/app/user/refresh_token"
    payload = {
        "app_ver": "wyze_developer_api",
        "app_version": "wyze_developer_api",
        "phone_id": "wyze_developer_api",
        "refresh_token": WYZE_REFRESH_TOKEN,
        "sc": "wyze_developer_api",
        "sv": "wyze_developer_api",
        "ts": 4070908800000
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(refresh_token_url, json=payload, headers=headers)
    if response.status_code == 200:
        response_data = response.json()
        data = response_data.get('data', {})
        WYZE_ACCESS_TOKEN = data.get('access_token')
        WYZE_REFRESH_TOKEN = data.get('refresh_token')
        # Save the new tokens to environment variables or a file
        os.environ['WYZE_ACCESS_TOKEN'] = WYZE_ACCESS_TOKEN
        os.environ['WYZE_REFRESH_TOKEN'] = WYZE_REFRESH_TOKEN
        with open('tokens.txt', 'w') as f:
            f.write(f"ACCESS_TOKEN={WYZE_ACCESS_TOKEN}\n")
            f.write(f"REFRESH_TOKEN={WYZE_REFRESH_TOKEN}\n")
        print("Tokens refreshed successfully.")
    else:
        print(f"Failed to refresh token: {response.status_code}")
        print("Response JSON:", response.json())

# Function to get the dominant color using K-means clustering
def get_dominant_color(image, k=4, image_processing_size=(100, 100)):
    # Resize image to reduce computation
    image = image.resize(image_processing_size)
    image = np.array(image)
    
    # Save the resized image for debugging purposes
    Image.fromarray(image).save("debug_resized_image.png")
    
    # Reshape image to be a list of pixels
    pixels = image.reshape((-1, 3))
    
    # Remove white colors and very bright colors
    pixels = np.array([pixel for pixel in pixels if np.all(pixel < 250)])
    
    # Perform K-means clustering
    kmeans = KMeans(n_clusters=k)
    kmeans.fit(pixels)
    colors = kmeans.cluster_centers_

    # Get the most frequent color
    labels = kmeans.labels_
    label_counts = np.bincount(labels)

    # Find the most frequent color index
    dominant_color_index = np.argmax(label_counts)
    dominant_color = colors[dominant_color_index]
    
    return tuple(int(c) for c in dominant_color)

# Function to set bulb color
def set_bulb_color(color):
    from wyze_sdk import Client
    from wyze_sdk.errors import WyzeApiError

    client = Client(token=WYZE_ACCESS_TOKEN)
    bulbs = [
        {'mac': '7C78B23FF2FC', 'model': 'WLPA19C'},  # Color Bulb 2
        {'mac': '7C78B2591F23', 'model': 'WLPA19C'},  # Color Bulb 1
    ]
    hex_color = f'{color[0]:02x}{color[1]:02x}{color[2]:02x}'

    try:
        for bulb in bulbs:
            client.bulbs.set_color(device_mac=bulb['mac'], device_model=bulb['model'], color=hex_color)
            bulb_info = client.bulbs.info(device_mac=bulb['mac'])
            print(f"Changed color of bulb {bulb['mac']} to: {bulb_info.color}")
    except WyzeApiError as e:
        print(f"Got an error: {e}")
        if e.response.status_code == 401:
            print("Access token expired. Refreshing token.")
            refresh_wyze_token()
            set_bulb_color(color)

# Monitor the current playing track
current_track_id = None
while True:
    print("Checking current playback state...")
    current_playback = sp.current_playback()
    print("Current playback state:", current_playback)
    if current_playback and current_playback['is_playing']:
        track = current_playback['item']
        track_id = track['id']
        if track_id != current_track_id:
            current_track_id = track_id
            
            print(f"Track changed to: {track['name']} by {track['artists'][0]['name']}")
            
            # Find the Spotify window
            windows = gw.getWindowsWithTitle('Spotify')
            if windows:
                spotify_window = windows[0]

                # Coordinates for the TV monitor positioned to the left of the main monitor
                left = spotify_window.left - 1920  # Adjust based on your TV monitor resolution
                top = spotify_window.top
                right = left + spotify_window.width
                bottom = top + spotify_window.height

                # Debugging: Print the coordinates
                print(f"Coordinates: left={left}, top={top}, right={right}, bottom={bottom}")

                with mss.mss() as sct:
                    monitor = {"top": top, "left": left, "width": spotify_window.width, "height": spotify_window.height}
                    screenshot = sct.grab(monitor)
                    img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)

                # Save screenshot for debugging purposes
                img.save("debug_screenshot.png")
                
                # Get the dominant color from the screenshot
                dominant_color = get_dominant_color(img)
                
                # Debugging: Print the dominant color
                print(f"Dominant color: {dominant_color}")
                
                # Set the bulb color to the dominant color
                set_bulb_color(dominant_color)
    else:
        print("No playback or playback is paused.")
    time.sleep(5)  # Wait for 5 seconds before checking again
