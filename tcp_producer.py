import io
import os
import socket
import time
import zlib

import requests
from PIL import Image
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth

import payload_ext


HOST = os.getenv("SYN_HOST", "127.0.0.1")
PORT = int(os.getenv("SYN_PORT", "5050"))
POLL_SECONDS = float(os.getenv("SYN_POLL_SECONDS", "1.0"))

SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID", "[your spotify client id]")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET", "[your spotify client secret]")
SPOTIPY_REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI", "[your spotify redirect uri]")


def spotify_client() -> Spotify:
    scope = "user-read-playback-state"
    return Spotify(
        auth_manager=SpotifyOAuth(
            client_id=SPOTIPY_CLIENT_ID,
            client_secret=SPOTIPY_CLIENT_SECRET,
            redirect_uri=SPOTIPY_REDIRECT_URI,
            scope=scope,
        )
    )


def dominant_color_from_track(track: dict) -> tuple[int, int, int]:
    images = track.get("album", {}).get("images", [])
    if not images:
        return (255, 255, 255)

    image_url = images[0]["url"]
    response = requests.get(image_url, timeout=10)
    response.raise_for_status()

    image = Image.open(io.BytesIO(response.content)).convert("RGB")
    image = image.resize((32, 32))
    pixels = list(image.getdata())

    filtered = [p for p in pixels if p[0] < 245 or p[1] < 245 or p[2] < 245]
    if not filtered:
        filtered = pixels

    r = sum(p[0] for p in filtered) // len(filtered)
    g = sum(p[1] for p in filtered) // len(filtered)
    b = sum(p[2] for p in filtered) // len(filtered)
    return (r, g, b)


def ensure_connection(sock: socket.socket | None) -> socket.socket:
    if sock is not None:
        return sock
    conn = socket.create_connection((HOST, PORT), timeout=5)
    conn.settimeout(5)
    return conn


def main() -> None:
    sp = spotify_client()
    current_track_id = None
    sock = None

    while True:
        try:
            playback = sp.current_playback()
            if playback and playback.get("is_playing"):
                track = playback["item"]
                track_id = track["id"]
                if track_id and track_id != current_track_id:
                    current_track_id = track_id
                    detect_ms = time.time_ns() // 1_000_000
                    rgb = dominant_color_from_track(track)
                    track_hash = zlib.crc32(track_id.encode("utf-8")) & 0xFFFFFFFF
                    payload = payload_ext.pack_rgb_payload(
                        rgb[0], rgb[1], rgb[2], track_hash, detect_ms
                    )

                    sock = ensure_connection(sock)
                    send_ms = time.time_ns() // 1_000_000
                    sock.sendall(payload)
                    print(
                        f"sent track={track['name']} rgb={rgb} bytes={len(payload)} "
                        f"detect_to_send_ms={send_ms - detect_ms}"
                    )
        except (requests.RequestException, socket.error, OSError) as exc:
            print(f"producer transport error: {exc}")
            if sock is not None:
                try:
                    sock.close()
                except OSError:
                    pass
            sock = None
        except Exception as exc:
            print(f"producer unexpected error: {exc}")

        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()
