# Music Player Daemon

A lightweight audio player daemon that streams YouTube audio through `ffplay`, with a Unix socket for control. Integrates with the Music Recommender web UI and Waybar.

## Quick Start

```bash
# 1. Start the daemon
MUSIC_PLAYER_PORT=18765 python3 -m player.daemon

# 2. Play a song
python3 -m player.ctl play lTRiuFIWV54 "1 AM Study Session" "Lofi Girl"

# 3. Control playback
python3 -m player.ctl pause      # pause
python3 -m player.ctl toggle     # play/pause
python3 -m player.ctl next       # next track
python3 -m player.ctl prev       # previous
python3 -m player.ctl stop       # stop
python3 -m player.ctl volume 80  # set volume (0-150)
python3 -m player.ctl status     # current status
python3 -m player.ctl queue      # show queue
python3 -m player.ctl clear      # clear queue
python3 -m player.ctl save mymix # save current queue as playlist
python3 -m player.ctl load mymix # load saved playlist
python3 -m player.ctl list       # list saved playlists
```

## Prerequisites

- `ffplay` (from `ffmpeg`)
- `yt-dlp`
- `deno` (JS runtime for YouTube extraction)
- Firefox with YouTube login (for cookie-based auth)

```bash
# Install deno
curl -fsSL https://deno.land/install.sh | sh
# Add to PATH
export PATH="$HOME/.deno/bin:$PATH"
```

## Configuration (Environment Variables)

| Variable | Default | Description |
|---|---|---|
| `MUSIC_PLAYER_SOCKET` | `/tmp/music-player.sock` | Unix socket path |
| `MUSIC_PLAYER_PORT` | (disabled) | TCP port for Docker/host bridge |
| `YTLP_PATH` | `yt-dlp` | yt-dlp executable |
| `YTLP_EXTRA` | `--js-runtimes deno --cookies-from-browser firefox` | Extra args for yt-dlp |

## Waybar Integration

Add this to `~/.config/waybar/config.jsonc`:

```json
"custom/music": {
    "exec": "python3 /path/to/player/waybar.py",
    "on-click": "python3 /path/to/player/ctl.py toggle",
    "on-click-right": "python3 /path/to/player/ctl.py stop",
    "on-scroll-up": "python3 /path/to/player/ctl.py next",
    "on-scroll-down": "python3 /path/to/player/ctl.py prev",
    "return-type": "json",
    "interval": 2
}
```

And style in `~/.config/waybar/style.css`:

```css
#custom-music {
    padding: 0 10px;
    font-size: 13px;
}
#custom-music.playing {
    color: #2ecc71;
}
#custom-music.paused {
    color: #f1c40f;
}
#custom-music.stopped {
    color: #555;
}
```

## Auto-start with systemd

Create `~/.config/systemd/user/music-player.service`:

```ini
[Unit]
Description=Music Player Daemon
After=network-online.target

[Service]
Type=simple
ExecStart=/home/YOU/.deno/bin/deno task -- /path/to/player/daemon.py
Environment=MUSIC_PLAYER_PORT=18765
Environment=PATH=/home/YOU/.deno/bin:/usr/local/bin:/usr/bin
Restart=on-failure

[Install]
WantedBy=default.target
```

```bash
systemctl --user enable --now music-player
```

## Web UI

The Music Recommender web UI at `http://localhost:8000` now has a **"Listen ♫"** button on every song card, plus a fixed bottom bar showing now-playing info with play/pause/next/prev/stop controls.

## Architecture

```
┌─────────────┐     Unix socket/TCP     ┌──────────────┐     ┌────────┐
│  Web UI     │◄──── FastAPI ──────────►│  Player      │────►│ ffplay │
│  (Browser)  │      proxy              │  Daemon      │     │ (audio)│
└─────────────┘                         │              │     └────────┘
                                        │  ┌─────────┐ │
┌─────────────┐                         │  │ Queue   │ │
│  Waybar     │◄──── Unix socket ───────┤  │ Playlist│ │
│  (widget)   │                         │  │ State   │ │
└─────────────┘                         │  └─────────┘ │
                                        └──────────────┘
```
