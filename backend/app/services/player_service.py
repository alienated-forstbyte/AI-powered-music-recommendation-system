import json
import os
import socket

SOCKET_PATH = os.environ.get("MUSIC_PLAYER_SOCKET", "/tmp/music-player.sock")
TCP_HOST = os.environ.get("MUSIC_PLAYER_HOST", "127.0.0.1")
TCP_PORT = os.environ.get("MUSIC_PLAYER_PORT")

_SOCKET_CACHE = None


def _get_socket():
    global _SOCKET_CACHE
    if _SOCKET_CACHE is not None:
        return _SOCKET_CACHE
    if TCP_PORT:
        addr = (TCP_HOST, int(TCP_PORT))
        _SOCKET_CACHE = ("tcp", addr)
        return _SOCKET_CACHE
    _SOCKET_CACHE = ("unix", SOCKET_PATH)
    return _SOCKET_CACHE


def daemon_request(cmd: str, **args) -> dict:
    stype, saddr = _get_socket()
    payload = json.dumps({"command": cmd, "args": args})
    try:
        if stype == "tcp":
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect(saddr)
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
    except FileNotFoundError:
        return {"error": f"daemon socket not found at {saddr}", "hint": "start with: python -m player.daemon"}
    except ConnectionRefusedError:
        return {"error": "daemon not running"}
    except Exception as e:
        return {"error": str(e)}


def play(video_id: str, title: str = "", channel: str = "") -> dict:
    return daemon_request("play", video_id=video_id, title=title, channel=channel)


def play_index(index: int) -> dict:
    return daemon_request("play_index", index=index)


def add(video_id: str, title: str = "", channel: str = "") -> dict:
    return daemon_request("add", video_id=video_id, title=title, channel=channel)


def pause() -> dict:
    return daemon_request("pause")


def toggle() -> dict:
    return daemon_request("toggle")


def next_track() -> dict:
    return daemon_request("next")


def prev_track() -> dict:
    return daemon_request("prev")


def stop() -> dict:
    return daemon_request("stop")


def status() -> dict:
    return daemon_request("status")


def volume(level: int | None = None) -> dict:
    return daemon_request("volume", level=level)


def queue() -> dict:
    return daemon_request("queue")


def remove(index: int) -> dict:
    return daemon_request("remove", index=index)


def clear() -> dict:
    return daemon_request("clear")


def save_playlist(name: str) -> dict:
    return daemon_request("save_playlist", name=name)


def load_playlist(name: str) -> dict:
    return daemon_request("load_playlist", name=name)


def list_playlists() -> dict:
    return daemon_request("list_playlists")
