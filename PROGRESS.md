# Music Player AI — Progress Log

## Project Goal

Build a music recommendation system with an audio player daemon so the user can hear music directly instead of opening YouTube links, with Waybar and web UI controls.

---

## Current Status

The recommendation engine and player daemon are fully functional.

YouTube audio extraction works via yt-dlp + deno + Firefox cookies for bot protection.

Audio playback uses ffplay.

Three interfaces can control the player:

- CLI (player.ctl)
- Waybar widget (player.waybar)
- Web UI (FastAPI proxy)

---

## Completed

### ML / Recommendation Engine

- sentence-transformers (all-MiniLM-L6-v2) → 384-dim embeddings → cosine similarity
- Full training pipeline: ml/pipeline.py
- Recommender class with cold-start fallback (popular songs for new users)
- SQLite play history + excluded tags per user
- Genre exclusion via feedback endpoint
- Model trained with 28 play events across 3 users (classical, metal, hip hop)
- 160-song catalog in data/raw/songs.json

### Player Daemon (player/)

- Unix socket + TCP dual transport for control
- Queue management with next/prev/remove/clear
- State persistence (~/.cache/music-player/state.json)
- Named playlist save/load
- ffplay subprocess management (SIGSTOP/SIGCONT for pause)
- Audio URL extraction via yt-dlp
- Graceful error handling: ConnectionResetError, ffplay exit codes, skip cooldown
- Debounce lock on next/prev to prevent rapid cycling

### CLI Controller (player/ctl.py)

- 15 commands: play, add, pause, toggle, next, prev, stop, volume, queue, remove, clear, status, save, load, list
- YouTube URL → video_id auto-extraction
- Play by queue index (numeric arg) or video_id (non-numeric)
- 10s socket timeout with helpful error messages

### Waybar Integration

- player/waybar.py outputs JSON with playing/paused/stopped/error CSS classes
- Click handlers for toggle, stop, next, prev
- 2-second refresh interval
- Auto-restart on script failure
- CSS styling in ~/.config/waybar/style.css

### Web UI Integration

- "Listen ♫" button on every song card (calls daemon play)
- Now-playing bar with ⏮ ⏸ ⏭ ⏹ controls
- Queue tab with song list + remove buttons
- Volume slider (0-150)
- Status polling every 2 seconds
- 15 FastAPI proxy endpoints in /player/

### Infrastructure

- Docker Compose with /tmp bind mount for daemon socket access
- Rootless Docker uid mapping handled
- Systemd user service for auto-start on login
- nohup start script at /tmp/start-player-daemon.sh

---

## Running

Daemon is alive and playing "1 AM Study Session" by Lofi Girl.

---

## Known Issues

- YouTube bot protection may occasionally block audio URL extraction
- deno + Firefox cookies required; no fallback for cookie expiry
- ffplay lacks IPC, so pause uses SIGSTOP (no metadata like seek position)
- Some video IDs may be blocked or region-restricted

---

## Notable Design Decisions

1. **ffplay over mpv** — Only ffplay was available; SIGSTOP/SIGCONT for pause control
2. **Dual transport** — Unix socket + TCP so Docker container can connect via /tmp bind mount
3. **YTLP_EXTRA env var** — yt-dlp args configurable per system at runtime
4. **Debounced next/prev** — 2s lock prevents rapid cycling through failed URLs
5. **Auto-restore state** — Daemon resumes queue and playback on restart if state file exists
6. **No auto-advance on errors** — ffplay exit codes checked: only clean exit (code 0) advances queue

---

## What's Next

- Add mpv as optional backend when available
- Expose player controls from Waybar more deeply (playlist selection)
- Improve cold-start for empty queues (add recommended songs directly)
- Handle cookie expiry gracefully (prompt to re-auth)
