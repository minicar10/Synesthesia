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
- Local TCP metadata transport between producer and consumer services
- Compact 16-byte packet encoding via a C extension (`payload_ext`)
- Timestamped latency logging with median/p95 reporting

---

## Tech Stack
- Python
- C (CPython extension)
- Spotify Web API
- Wyze API
- REST APIs
- Basic image analysis (album art color extraction)
- Raw TCP sockets (localhost service-to-service transport)

---

## Architecture Overview
1. Authenticate with Spotify using OAuth 2.0 and refresh tokens  
2. Poll the currently playing track and retrieve album artwork  
3. Extract dominant color information from the artwork  
4. Pack RGB + metadata into a compact binary payload using `payload_ext` (C extension)  
5. Stream payloads over localhost TCP to the lighting consumer  
6. Apply Wyze smart bulb commands and log end-to-end latency  

---

## TCP + C Extension Workflow
Prerequisite on Windows:
- Install "Microsoft C++ Build Tools" (Visual C++ 14.0+) so CPython extensions can compile.

1. Build the C extension:
   `python setup_payload_ext.py build_ext --inplace`
2. Start consumer service (applies bulb commands and logs latency):
   `python tcp_consumer.py`
3. Start producer service (Spotify poller that sends packets):
   `python tcp_producer.py`
4. Generate latency summary:
   `python latency_report.py`

Environment variables:
- `SPOTIPY_CLIENT_ID`, `SPOTIPY_CLIENT_SECRET`, `SPOTIPY_REDIRECT_URI`
- `WYZE_ACCESS_TOKEN`
- `WYZE_BULBS` format: `mac1:model1,mac2:model2`
- Optional: `SYN_HOST`, `SYN_PORT`, `SYN_POLL_SECONDS`, `SYN_LATENCY_LOG`

---

## Design Notes
- Uses polling rather than event streaming due to Spotify API limitations
- Separates authentication, device control, and lighting logic into modular scripts
- Designed for extensibility to support additional lighting effects or devices

---

## Disclaimer
This project was built as a personal automation and API-integration exercise.
It is not intended for production use.
