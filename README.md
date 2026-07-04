# Music Player AI

> A music recommendation system with a local audio player daemon. Search YouTube, get AI recommendations, and listen directly — no browser tabs needed.

## Overview

Two systems in one:

**Recommendation Engine** — sentence-transformers NLP model that learns your taste from play history and recommends unseen songs.

**Player Daemon** — streams YouTube audio through ffplay, controllable from the web UI, Waybar, or terminal.

## Quick Start

```bash
# Start the backend
make up

# Seed songs (first time)
python -m ml.data_ingestion.fetch_songs

# Train the model
make train

# Start the player daemon
cd player && ./start-daemon.sh

# Play a song
python -m player.ctl play lTRiuFIWV54 "1 AM Study Session" "Lofi Girl"
```

Open http://localhost:8000

## Interfaces

| Interface | Purpose |
|-----------|---------|
| Web UI (port 8000) | Search, recommend, Listen button, queue, volume |
| Waybar widget | Now-playing, play/pause, next/prev from status bar |
| CLI (`player.ctl`) | 15 commands for queue management and playback |
| API | REST endpoints for search, recommendations, player control |

## Technology Stack

### Backend
- FastAPI / Uvicorn
- SQLite (play history)
- sentence-transformers (all-MiniLM-L6-v2)
- yt-dlp (YouTube search + audio extraction)

### Player
- ffplay (FFmpeg audio playback)
- yt-dlp + deno (YouTube audio URLs)
- Unix socket + TCP (control plane)

### Frontend
- Static HTML/JS (no framework)
- Waybar JSON module

### Observability
- Grafana + Loki
- Pre-built dashboard

## Project Layout

```
├── backend/
│   └── app/
│       ├── main.py             FastAPI app
│       ├── routes/             search, play, recommend, feedback, player
│       ├── services/           youtube, logging, user, feedback
│       └── static/index.html   Web UI
├── player/
│   ├── daemon.py               Audio player daemon
│   ├── ctl.py                  CLI controller
│   ├── waybar.py               Waybar JSON output
│   └── start-daemon.sh         Entrypoint for systemd/manual
├── ml/
│   ├── pipeline.py             Full training pipeline
│   ├── data_ingestion/         Fetch song metadata
│   ├── training/               Feature engineering + training
│   └── inference/              Recommender class + model.pkl
├── data/
│   ├── raw/songs.json          Song catalog (160+ songs)
│   └── processed/              User history + SQLite DB
├── docker-compose.yaml         Backend + Loki + Grafana
└── Makefile
```

## API

See API.md

## Architecture

See ARCHITECTURE.md

## Database

See DATABASE.md

## Development Plan

See PLAN.md
