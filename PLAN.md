# Music Player AI — Development Plan

## Vision

A music recommendation system paired with an audio player daemon so users never need to open YouTube links or manually queue songs.

The system learns user preferences from play history and recommends unseen songs using NLP-powered similarity.

Audio playback is controlled from the web UI, Waybar, or CLI.

---

## Guiding Principles

### No External API Keys

YouTube search and audio extraction use yt-dlp.

No YouTube Data API v3 key required.

---

### Modular Player Architecture

The player daemon is a standalone process controlled via Unix socket or TCP.

The web UI, CLI, and Waybar are interchangeable control surfaces.

Adding a new control surface requires no daemon changes.

---

### Content-Based Filtering

No collaborative filtering.

Recommendations are based on song metadata (title, channel, tags) only.

Embeddings via sentence-transformers.

---

## Phase 1: Foundation

### Backend

- FastAPI
- SQLite (play history)
- JSON files (song catalog)
- sentence-transformers ML model

### Services

- YouTube search via yt-dlp
- Play event logging
- User history storage

Deliverable: Running web app with search and play logging.

---

## Phase 2: ML Pipeline

### Components

- Data ingestion: reads SQLite logs, fetches song metadata
- Feature engineering: builds user-song matrix
- Training: sentence-transformers embeddings → similarity
- Inference: Recommender class with cold-start fallback

### Training Flow

```
SQLite play history
  ↓
Fetch new song metadata via yt-dlp
  ↓
Enrich song catalog
  ↓
Compute embeddings for all songs
  ↓
For each user: mean of played song embeddings → cosine similarity → top-K unseen
  ↓
Save model.pkl
```

Deliverable: Personalized recommendations for each user.

---

## Phase 3: Player Daemon

### Components

- player/daemon.py — async daemon with Unix socket + TCP
- player/ctl.py — CLI controller
- player/waybar.py — Waybar JSON output

### Control Plane

```
Unix socket (/tmp/music-player.sock)
TCP port (18765)
Both simultaneously
```

### Playback

- ffplay for audio
- yt-dlp for YouTube audio URL extraction
- deno + Firefox cookies for bot protection
- Queue management with state persistence

### Commands

- play, add, pause, toggle, next, prev, stop
- volume, queue, remove, clear, status
- save, load, list (named playlists)

Deliverable: Music plays through speakers, controllable from all three interfaces.

---

## Phase 4: Web UI Integration

### Static Frontend

- FastAPI serves index.html (no JS framework)
- Search + recommend tabs
- "Listen ♫" button per song
- Now-playing bar with controls
- Queue tab
- Status polling

### Backend Proxy

- /player/ routes forward commands to daemon
- Auto-detects Unix socket or TCP

Deliverable: Full play control from the browser.

---

## Phase 5: Infrastructure

### Docker

- Backend + Loki + Grafana in docker-compose
- /tmp bind mount for daemon socket
- Rootless Docker uid mapping

### Systemd

- User service for auto-start on login
- Restart on failure

Deliverable: Player daemon survives reboots.

---

## Phase 6: Polish

### Error Handling

- yt-dlp failure → skip cooldown (3s)
- ffplay crash → no auto-advance (only clean exit advances)
- ConnectionResetError → graceful handler
- CLI timeout → 10s with helpful hint

### Input Handling

- YouTube URL → video_id auto-extraction
- Play by queue index or video_id

Deliverable: Robust player that handles transient failures.

---

## Future Ideas

### Backend Enhancements

- mpv backend for better IPC
- Volume normalization across songs
- Crossfade between tracks

### Frontend Enhancements

- Drag-to-reorder queue
- Playlist CRUD from web UI
- Keyboard shortcuts (Space = toggle, etc.)

### ML Enhancements

- Play count weighting in embeddings
- Session-aware recommendations (don't recommend same artist twice in a row)
- Real-time retraining on new play events

### Distribution

- Flatpak / Snap for easy install
- MPRIS D-Bus interface for desktop environment integration
- Spotify/Last.fm import for seed history
