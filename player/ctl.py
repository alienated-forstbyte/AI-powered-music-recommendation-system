#!/usr/bin/env python3
"""CLI controller for the music player daemon."""

import json
import os
import re
import socket
import sys

SOCKET_PATH = os.environ.get("MUSIC_PLAYER_SOCKET", "/tmp/music-player.sock")


def extract_video_id(video_id: str) -> str:
    m = re.search(r"(?:v=|youtu\.be/|/shorts/|music\.youtube\.com/watch\?v=)([a-zA-Z0-9_-]{11})", video_id)
    if m:
        return m.group(1)
    if re.match(r"^[a-zA-Z0-9_-]{11}$", video_id):
        return video_id
    return video_id


def send(cmd: str, **args) -> dict:
    payload = json.dumps({"command": cmd, "args": args})
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.settimeout(10)
    try:
        sock.connect(SOCKET_PATH)
    except FileNotFoundError:
        print(json.dumps({"error": "daemon not running", "hint": "start with: python -m player.daemon"}))
        sys.exit(1)
    except ConnectionRefusedError:
        print(json.dumps({"error": "daemon socket refused"}))
        sys.exit(1)
    sock.sendall(payload.encode())
    sock.shutdown(socket.SHUT_WR)
    data = b""
    try:
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            data += chunk
    except socket.timeout:
        print(json.dumps({"error": "daemon timed out", "hint": "the daemon might be busy starting playback"}))
        sys.exit(1)
    sock.close()
    if not data:
        print(json.dumps({"error": "empty response from daemon"}))
        sys.exit(1)
    return json.loads(data.decode())


def print_status(resp):
    status = resp.get("status", "")
    if status == "playing":
        s = resp.get("song", {})
        print(f"▶  {s.get('title', '?')}")
    elif status == "paused":
        s = resp.get("song", {})
        print(f"⏸  {s.get('title', '?')}")
    elif status == "stopped":
        print("⏹  Stopped")
    elif "error" in resp:
        print(f"✗ {resp['error']}")
    else:
        print(json.dumps(resp, indent=2) if len(json.dumps(resp)) < 200 else resp.get("status", json.dumps(resp)))


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m player.ctl <command> [args]")
        print()
        print("Commands:")
        print("  play <video_id> [title] [channel]   Play a song (adds to queue)")
        print("  play <index>                        Play song at queue index (numeric only)")
        print("  add <video_id> [title] [channel]     Add song to queue")
        print("  pause                                 Toggle pause/resume")
        print("  toggle                                Toggle pause/resume")
        print("  next                                  Next track")
        print("  prev                                  Previous track")
        print("  stop                                  Stop playback")
        print("  volume <level>                        Set volume (0-150)")
        print("  queue                                 Show queue")
        print("  remove <index>                        Remove from queue")
        print("  clear                                 Clear queue")
        print("  status                                Current status")
        print("  save <name>                           Save current queue as playlist")
        print("  load <name>                           Load a saved playlist")
        print("  list                                  List saved playlists")
        print("  user [user_id|list|next]               Show/set/cycle/list recommendation users")
        return

    cmd = sys.argv[1]
    args = sys.argv[2:]

    if cmd == "play":
        if args[0].isdigit() and len(args) == 1:
            resp = send("play_index", index=int(args[0]))
        else:
            resp = send("play", video_id=extract_video_id(args[0]), title=args[1] if len(args) > 1 else "", channel=args[2] if len(args) > 2 else "")
    elif cmd == "add":
        resp = send("add", video_id=extract_video_id(args[0]), title=args[1] if len(args) > 1 else "", channel=args[2] if len(args) > 2 else "")
    elif cmd == "pause":
        resp = send("pause")
    elif cmd == "toggle" or cmd == "playpause":
        resp = send("toggle")
    elif cmd == "next":
        resp = send("next")
    elif cmd == "prev" or cmd == "previous":
        resp = send("prev")
    elif cmd == "stop":
        resp = send("stop")
    elif cmd == "volume":
        resp = send("volume", level=int(args[0]) if args else None)
    elif cmd == "queue":
        resp = send("queue")
    elif cmd == "remove":
        resp = send("remove", index=int(args[0]))
    elif cmd == "clear":
        resp = send("clear")
    elif cmd == "status":
        resp = send("status")
    elif cmd == "save":
        resp = send("save_playlist", name=args[0])
    elif cmd == "load":
        resp = send("load_playlist", name=args[0])
    elif cmd == "list":
        resp = send("list_playlists")
    elif cmd == "user":
        from player.user_state import get_current_user, set_current_user, cycle_user, list_users
        if not args:
            print(f"Current user: {get_current_user()}")
            return
        if args[0] == "list":
            for u in list_users():
                print(f"  {u}")
            return
        if args[0] == "next":
            next_u = cycle_user()
            print(f"Switched to user: {next_u}")
            return
        set_current_user(args[0])
        print(f"User set to: {args[0]}")
        return
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)

    if cmd in ("status", "play", "pause", "toggle", "next", "prev", "stop"):
        print_status(resp)
    elif cmd == "queue":
        q = resp.get("queue", [])
        idx = resp.get("current_index")
        print(f"Queue ({len(q)} songs):")
        for i, s in enumerate(q):
            marker = "→ " if i == idx else "  "
            print(f"  {marker}{i}. {s.get('title', s['video_id'])}")
    elif cmd == "list":
        pl = resp.get("playlists", [])
        print("Saved playlists:")
        for p in pl:
            print(f"  {p}")
    else:
        if "error" in resp:
            print(f"Error: {resp['error']}")
        else:
            print(resp.get("status", json.dumps(resp)))


if __name__ == "__main__":
    main()
