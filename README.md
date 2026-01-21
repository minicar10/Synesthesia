# Synesthesia — Spotify × Wyze Smart Lighting Integration

Synesthesia is a Python-based automation project that synchronizes Wyze smart bulbs
with Spotify playback data to create dynamic, music-responsive lighting effects.

## Features
- Secure OAuth 2.0 authentication with Spotify
- Real-time polling of track metadata and album art
- Automated color transitions and multi-bulb effects
- Modular Wyze device discovery and control
- Configurable lighting presets (disco, ambient, static)

## Tech Stack
- Python
- Spotify Web API
- Wyze API
- REST APIs
- Image analysis (album art processing)

## How It Works
1. Authenticates with Spotify using OAuth 2.0 and refresh tokens
2. Polls the currently playing track and album artwork
3. Extracts dominant colors from artwork
4. Sends lighting commands to Wyze smart bulbs

## Notes
This project was built as a personal automation experiment focused on API
integration, authentication flows, and real-time device control.
