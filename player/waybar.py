#!/usr/bin/env python3
"""Waybar custom module script for music player control.
Outputs JSON for Waybar's custom module with click actions.

Add to ~/.config/waybar/config.jsonc:
  "custom/music": {
    "exec": "python3 /path/to/player/waybar.py",
    "on-click": "python3 /path/to/player/ctl.py toggle",
    "on-click-right": "python3 /path/to/player/ctl.py stop",
    "on-scroll-up": "python3 /path/to/player/ctl.py next",
    "on-scroll-down": "python3 /path/to/player/ctl.py prev",
    "return-type": "json",
    "interval": 2
  }
"""

import json
import os
import socket
import sys

SOCKET_PATH = os.environ.get("MUSIC_PLAYER_SOCKET", "/tmp/music-player.sock")


def send(cmd: str, **args) -> dict | None:
    payload = json.dumps({"command": cmd, "args": args})
    try:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.settimeout(2)
        sock.connect(SOCKET_PATH)
        sock.sendall(payload.encode())
        sock.shutdown(socket.SHUT_WR)
        data = b""
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            data += chunk
        sock.close()
        return json.loads(data.decode())
    except (FileNotFoundError, ConnectionRefusedError, OSError, json.JSONDecodeError):
        return None


def waybar_output():
    resp = send("status")
    if resp is None:
        print(json.dumps({"text": "♫ --", "class": "stopped", "tooltip": "Player not running"}))
        return

    status = resp.get("status", "stopped")
    song = resp.get("song")
    vol = resp.get("volume", 100)
    qlen = resp.get("queue_length", 0)

    if status == "playing" and song:
        title = song.get("title", song["video_id"])
        channel = song.get("channel", "")
        text = f"♫ {title[:40]}"
        cls = "playing"
        tooltip = f"Now Playing: {title}\n{channel}\nVolume: {vol}%  |  Queue: {qlen} songs"
    elif status == "paused" and song:
        title = song.get("title", song["video_id"])
        text = f"♫ {title[:30]} ⏸"
        cls = "paused"
        tooltip = f"Paused: {title}\nVolume: {vol}%  |  Queue: {qlen} songs"
    else:
        text = "♫ Stopped"
        cls = "stopped"
        tooltip = f"Player stopped | Queue: {qlen} songs"

    print(json.dumps({"text": text, "class": cls, "tooltip": tooltip}))


if __name__ == "__main__":
    waybar_output()
