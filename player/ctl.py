#!/usr/bin/env python3
"""CLI controller for the music player daemon."""

import json
import os
import socket
import sys

SOCKET_PATH = os.environ.get("MUSIC_PLAYER_SOCKET", "/tmp/music-player.sock")


def send(cmd: str, **args) -> dict:
    payload = json.dumps({"command": cmd, "args": args})
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.settimeout(5)
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
    while True:
        chunk = sock.recv(4096)
        if not chunk:
            break
        data += chunk
    sock.close()
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
        return

    cmd = sys.argv[1]
    args = sys.argv[2:]

    if cmd == "play":
        resp = send("play", video_id=args[0], title=args[1] if len(args) > 1 else "", channel=args[2] if len(args) > 2 else "")
    elif cmd == "add":
        resp = send("add", video_id=args[0], title=args[1] if len(args) > 1 else "", channel=args[2] if len(args) > 2 else "")
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
