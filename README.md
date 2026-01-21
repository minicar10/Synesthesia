# Synesthesia: Spotify + Wyze Smart Lighting Integration

Synesthesia is a Python-based automation project that synchronizes Wyze smart bulbs
with Spotify playback data to create dynamic, music-responsive lighting effects.

---

## Features
- Secure OAuth 2.0 authentication with Spotify
- Polling-based retrieval of track metadata and album art
- Automated color transitions and multi-bulb lighting effects
- Modular Wyze device discovery and control
- Configurable lighting presets (disco, ambient, static)

---

## Tech Stack
- Python
- Spotify Web API
- Wyze API
- REST APIs
- Basic image analysis (album art color extraction)

---

## Architecture Overview
1. Authenticate with Spotify using OAuth 2.0 and refresh tokens  
2. Poll the currently playing track and retrieve album artwork  
3. Extract dominant color information from the artwork  
4. Translate color data into Wyze smart bulb commands  

---

## Design Notes
- Uses polling rather than event streaming due to Spotify API limitations
- Separates authentication, device control, and lighting logic into modular scripts
- Designed for extensibility to support additional lighting effects or devices

---

## Disclaimer
This project was built as a personal automation and API-integration exercise.
It is not intended for production use.
