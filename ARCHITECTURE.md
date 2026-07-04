# Music Player AI — Architecture

## Overview

Two independent systems that communicate through a shared control plane:

1. **Recommendation Engine** — FastAPI + ML pipeline
2. **Player Daemon** — standalone audio player with multiple control surfaces

The player daemon does not know about recommendations.

The recommendation engine does not know about audio playback.

They share the song catalog and the Unix socket.

---

## High-Level Architecture

```
User
  │
  ├── Browser ─── FastAPI (port 8000)
  │                   ├── /search/      → yt-dlp
  │                   ├── /play/        → SQLite + Loki
  │                   ├── /recommend/   → ML model
  │                   ├── /feedback/    → excluded tags
  │                   └── /player/      ─→ Unix socket ────┐
  │                                                         │
  ├── Waybar ──────── player/waybar.py  ─→ Unix socket ─────┤
  │                                                         │
  └── Terminal ────── python -m player.ctl ─→ Unix socket ──┤
                                                            │
                                            Player Daemon   │
                                            (player/         │
                                             daemon.py)      │
                                                │            │
                                             ffplay (audio)
```

---

## Components

### Recommendation Engine

```
backend/
  app/
    main.py             FastAPI app factory
    routes/
      search.py         YouTube search via yt-dlp
      play.py           Log play events
      recommend.py      ML inference endpoint
      feedback.py       Handle skip/dislike feedback
      player.py         Proxy to daemon (15 endpoints)
    services/
      youtube_service.py
      logging_service.py   Loki log integration
      user_service.py      SQLite play history
      feedback_service.py  Excluded tags
    static/
      index.html        Single-page web UI

ml/
  pipeline.py           Full training pipeline
  data_ingestion/       Fetch song metadata, build dataset
  training/             Feature engineering, embedding training
  inference/            Recommender class + model.pkl
```

### Player Daemon

```
player/
  daemon.py             Async Unix socket + TCP daemon
  ctl.py                CLI controller (15 commands)
  waybar.py             Waybar JSON output
  start-daemon.sh       systemd entrypoint
  README.md             Player-specific docs
```

---

## Data Flow

### Search

```
Browser → GET /search/?query=lofi&max_results=5
  → youtube_service.search_youtube()
    → yt-dlp ytsearch5:lofi
  → Returns JSON results
```

### Play + Log

```
Browser → POST /play/?video_id=abc&user_id=user_1
  → log_event("play", ...)       → Loki
  → log_user_play(user_id, id)   → SQLite
  → Returns { "status": "logged" }
```

### Recommend

```
Browser → GET /recommend/user?user_id=user_1&top_k=5
  → Recommender.recommend_for_user()
    → Load user history from SQLite
    → Mean of played song embeddings
    → Cosine similarity with all songs
    → Exclude skipped/disliked tags
    → Return top-K unseen songs
```

### Player Control

```
Browser/Waybar/CLI → Unix socket/TCP
  → JSON payload: { "command": "play", "args": {...} }
  → Daemon dispatches to handler
    → yt-dlp extracts audio URL
    → Spawns ffplay subprocess
  → Returns JSON response
```

---

## Communication

### Unix Socket

Path: /tmp/music-player.sock

Permissions: 0666

Protocol: JSON over streaming socket

Request format:
```
{ "command": "<cmd>", "args": { ... } }
```

Response format:
```
{ "status": "...", ... }
```

### TCP Fallback

Port: 18765 (configurable via MUSIC_PLAYER_PORT)

Host: 0.0.0.0

Used when the daemon is accessed from Docker container.

---

## State Persistence

### Player State

File: ~/.cache/music-player/state.json

Persisted on every queue change.

Restored on daemon start.

Contains: queue, current_index, volume

### User History

File: data/processed/user_history.json

SQLite: data/processed/plays.db

Updated on every play event.

### Song Catalog

File: data/raw/songs.json

Updated during training pipeline.

---

## Security Model

- No authentication on daemon socket (local only)
- Web UI proxy adds no auth (internal network)
- Docker rootless mode for container isolation
- Firefox cookies stored in user home only
