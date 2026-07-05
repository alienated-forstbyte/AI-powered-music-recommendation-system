# Music Player AI — Progress Log

## Project Goal

Build a music recommendation system with an audio player daemon so the user can hear music directly instead of opening YouTube links, with Waybar and web UI controls.

---

## Current Status

The recommendation engine and player daemon are fully functional.

YouTube audio extraction works via yt-dlp + deno + Firefox cookies for bot protection.

Audio playback uses ffplay.

Four interfaces can control the player:

- CLI (player.ctl)
- Waybar widget (player.waybar)
- Web UI (FastAPI proxy)
- Collection status page (localhost:8000/status)

---

## Completed

### ML / Recommendation Engine

- sentence-transformers (all-MiniLM-L6-v2) → 384-dim embeddings → cosine similarity
- Full training pipeline: ml/pipeline.py
- Recommender class with cold-start fallback (popular songs for new users)
- SQLite play history + excluded tags per user
- Genre exclusion via feedback endpoint
- Model trained with 52 play events across 17 users
- 172-song catalog in data/raw/songs.json (includes 12 Japanese pop songs)
- User `user_4` created with Japanese pop play history (YOASOBI, Kenshi Yonezu, LiSA, Ado, etc.)

### Player Daemon (player/)

- Unix socket + TCP dual transport for control
- Queue management with next/prev/remove/clear
- State persistence (~/.cache/music-player/state.json)
- Named playlist save/load
- ffplay subprocess management (SIGSTOP/SIGCONT for pause)
- Audio URL extraction via yt-dlp
- Graceful error handling: ConnectionResetError, ffplay exit codes, skip cooldown
- Debounce lock on next/prev to prevent rapid cycling
- **Collection mode** — `--collection` flag loads songs from `data/collection.json`, tracks plays/skips per song, auto-removes after 3 skips, reshuffles on exhaustion
- **Collection commands** — `collection_add`, `collection_add_url`, `collection_stats`, `collection_list`, `collection_reset_skips`
- Skip recording deferred after reshuffle to prevent self-exclusion bug
- Properly drains stuck state when queue empties during reshuffle

### CLI Controller (player/ctl.py)

- 16 commands: play, add, pause, toggle, next, prev, stop, volume, queue, remove, clear, status, save, load, list, user
- YouTube URL → video_id auto-extraction
- Play by queue index (numeric arg) or video_id (non-numeric)
- 10s socket timeout with helpful error messages
- `user` command: show/set/list/next recommendation user

### User State Management (player/user_state.py)

- Current user persisted to `~/.cache/music-player/current_user`
- `get_current_user()`, `set_current_user()`, `list_users()`, `cycle_user()`, `cycle_fav_user()`
- Favorites list: `user_2`, `user_3`, `user_4`

### Waybar Integration

- **player/waybar.py** — outputs JSON with playing/paused/stopped CSS classes, click handlers for toggle/stop/next/prev, shows current user in text and tooltip
- **player/waybar-user.py** — dedicated user switcher module, shows `👤 user  ★☆☆` with per-user click targets (left=user_2, right=user_3, middle=user_4)
- 2-second refresh interval
- CSS styling in ~/.config/waybar/style.css

### Web UI Integration

- "Listen ♫" button on every song card (calls daemon play)
- Now-playing bar with ⏮ ⏸ ⏭ ⏹ controls
- Queue tab with song list + remove buttons
- Volume slider (0-150)
- Status polling every 2 seconds
- 15 FastAPI proxy endpoints in /player/
- **User dropdown** with favorites (user_2/3/4 highlighted) replaces text input
- **Status page** at `/status` — song table with skip counts, play counts, reset buttons, player info bar, user selector

### Collection Status Page (localhost:8000/status)

- Stats bar: total songs, active, removed
- Song table with thumbnail, title, channel, plays, color-coded skips, reset button per song
- Player info bar: mode badge, current song, queue count, active user
- Reset button calls `POST /player/collection/reset_skips?video_id=xxx`
- Refresh button, auto-loads on page open

### Infrastructure

- Docker Compose with /tmp bind mount for daemon socket access
- Rootless Docker uid mapping handled
- Systemd user service for auto-start on login
- nohup start script at /tmp/start-player-daemon.sh

---

## Running

Daemon is alive in collection mode.

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
7. **Deferred skip recording** — `_record_skip_if_needed` runs after reshuffle so skip increments don't poison the active pool
8. **State file over daemon for user** — Current user stored in `~/.cache/music-player/current_user`, not in daemon, keeping the daemon agnostic to recommendation concepts

---

## What's Next

- Add mpv as optional backend when available
- Improve cold-start for empty queues (add recommended songs directly)
- Handle cookie expiry gracefully (prompt to re-auth)
