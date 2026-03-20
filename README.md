# ISS Tracker Web App

A small Flask-based project for tracking the International Space Station (ISS), showing live position updates, displaying ISS facts, and listing upcoming visible ISS passes over Zurich.

## Features

- Flask web app with multiple pages
- Live ISS latitude / longitude updates
- Turtle-based ISS map tracker
- Zurich ISS pass prediction using `skyfield`
- Static assets and HTML templates separated into standard Flask folders

## Project structure

```text
iss-tracker-repo/
├── app.py
├── run_original.py
├── zurich.py
├── requirements.txt
├── .gitignore
├── README.md
├── templates/
│   ├── index.html
│   ├── iss_facts.html
│   └── launch_and_track.html
├── static/
│   ├── ISS_emblem.png
│   ├── iss.gif
│   ├── map.gif
│   ├── xingkong.jpg
│   └── iss_position.json
├── data/
│   ├── iss.txt
│   ├── stations.txt
│   └── ISS Trajectory Data.txt
└── archive_Homepage.html
```

## Run locally

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start the Flask app:

```bash
python app.py
```

4. Open the browser at:

```text
http://127.0.0.1:5000/
```

## Important notes

- `app.py` currently starts Flask on port `80`, which often requires admin privileges. For local development, port `5000` is recommended.
- `run_original.py` uses `turtle`, so it needs a GUI environment.
- `zurich.py` contains an embedded OpenWeatherMap API key. That should be moved to an environment variable before publishing publicly.
- `start_iss.command` was not included because it references `iss_server.py`, which is not present in the uploaded files.
- `Homepage.html` appears to be an older standalone page and was placed in the archive area instead of the main app flow.

## Suggested next cleanup

- Move secrets into `.env`
- Rename `run_original.py` to something clearer like `tracker.py`
- Store generated files separately from source-controlled files
- Add screenshots to the README
- Add a license
