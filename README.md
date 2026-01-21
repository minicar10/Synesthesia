# Synesthesia | Spotify-Wyze Integration 💡🎧

Synesthesia is a high-performance Python automation tool that synchronizes Wyze smart bulbs with real-time Spotify playback data.

## 🚀 Key Features
* [cite_start]**Low-Latency Sync:** Optimized image processing pipeline analyzing album art in under 500ms.
* [cite_start]**OAuth 2.0 Security:** Robust integration layer handling token refresh logic for secure authentication.
* [cite_start]**Real-time Polling:** Utilizes Spotify REST API polling endpoints for instant lighting transitions[cite: 34].

## 🛠️ Technical Stack
* [cite_start]**Language:** Python [cite: 10]
* [cite_start]**APIs:** Spotify Web API, Wyze Labs REST API [cite: 34]
* **Key Libraries:** Requests, Pillow (for image processing), Spotipy

## 📦 Installation & Setup
1. Clone the repository: `git clone https://github.com/minicar10/Synesthesia.git`
2. Install dependencies: `pip install -r requirements.txt`
3. Configure your `.env` file with Spotify Client ID and Wyze credentials.
4. Run the application: `python src/main.py`
