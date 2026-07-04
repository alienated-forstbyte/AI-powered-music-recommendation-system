# Music Player AI — Database Design

---

## Overview

Two storage systems:

- SQLite — user play history, excluded tags
- JSON files — song catalog, player state, named playlists

No relational database. No migrations.

---

## SQLite

File

data/processed/plays.db

### plays

Stores individual play events for ML training.

Columns

- id — auto-increment
- user_id — text (user_1, user_2, user_3, etc.)
- video_id — YouTube video ID
- timestamp — ISO 8601

Indexes

- (user_id)
- (video_id)

### excluded_tags

Tracks skipped/disliked tags per user for filtering recommendations.

Columns

- id — auto-increment
- user_id — text
- tag — tag name (e.g. "metal", "classical")
- action — "skip" or "dislike"
- skip_count — integer, incremented on skip
- created_at — ISO 8601

A tag is excluded when skip_count >= SKIP_LIMIT (3).

---

## JSON Files

### Song Catalog

File

data/raw/songs.json

Structure

```json
[
  {
    "video_id": "lTRiuFIWV54",
    "title": "1 AM Study Session",
    "channel": "Lofi Girl",
    "tags": ["lofi", "chill", "study"],
    "duration": 3673
  }
]
```

Contains 160+ songs.

Tags are manually curated or extracted from YouTube metadata.

### User Play History

File

data/processed/user_history.json

Structure

```json
{
  "user_1": ["lTRiuFIWV54", "jfKfPfyJRdk", ...],
  "user_2": [...]
}
```

Built from SQLite during training pipeline.

### Player State

File

~/.cache/music-player/state.json

Structure

```json
{
  "queue": [
    { "video_id": "lTRiuFIWV54", "title": "1 AM Study Session", "channel": "Lofi Girl" }
  ],
  "current_index": 0,
  "volume": 100
}
```

Persisted on every queue change.

Restored on daemon start.

### Named Playlists

Directory

~/.cache/music-player/playlists/

Files

One JSON file per playlist (e.g. mymix.json).

Structure

```json
{
  "name": "mymix",
  "songs": [
    { "video_id": "...", "title": "...", "channel": "..." }
  ]
}
```

---

## Data Flow

```
Play event (web UI)
  → POST /play/ → SQLite (plays table)
  → Loki (log aggregation)

Training pipeline
  → SQLite → user_history.json
  → yt-dlp → new song metadata
  → data/raw/songs.json updated
  → Embeddings computed → model.pkl

Player queue
  → daemon.py manages in memory
  → state.json for persistence
  → playlists/*.json for named playlists
```

---

## No Data Loss Scenarios

- Player daemon crash → state restored from state.json on restart
- Backend restart → SQLite persistent on disk
- Docker container rebuild → data/ directory bind-mounted
