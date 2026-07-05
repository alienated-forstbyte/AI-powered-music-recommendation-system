import json
import os
import random
import subprocess
import time
from pathlib import Path

COLLECTION_PATH = Path(__file__).parent.parent / "data" / "collection.json"
SKIP_THRESHOLD = 3

def load():
    if not COLLECTION_PATH.exists():
        return []
    with open(COLLECTION_PATH) as f:
        return json.load(f)

def save(songs):
    COLLECTION_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(COLLECTION_PATH, "w") as f:
        json.dump(songs, f, indent=2)

def add(song):
    songs = load()
    songs.append(song)
    save(songs)

def active_pool(songs):
    return [s for s in songs if s.get("skips", 0) < SKIP_THRESHOLD]

def shuffled_playlist():
    pool = active_pool(load())
    random.shuffle(pool)
    return pool

def _match_song(a, b):
    if a.get("source") == "url" and b.get("source") == "url":
        return a.get("url") == b.get("url")
    return a.get("video_id") and b.get("video_id") and a["video_id"] == b["video_id"]

def record_skip(song):
    songs = load()
    for s in songs:
        if _match_song(s, song):
            s["skips"] = s.get("skips", 0) + 1
            break
    save(songs)

def record_play(song):
    songs = load()
    for s in songs:
        if _match_song(s, song):
            s["plays"] = s.get("plays", 0) + 1
            break
    save(songs)

def add_from_youtube(video_id, title="", channel=""):
    try:
        result = subprocess.run(
            ["yt-dlp", "--print", "duration",
             "--js-runtimes", "deno", "--cookies-from-browser", "firefox",
             f"https://youtube.com/watch?v={video_id}"],
            capture_output=True, text=True, timeout=30
        )
        duration = int(float(result.stdout.strip())) if result.stdout.strip() else 0
    except Exception:
        duration = 0
    if not title:
        try:
            result = subprocess.run(
                ["yt-dlp", "--print", "title",
                 "--js-runtimes", "deno", "--cookies-from-browser", "firefox",
                 f"https://youtube.com/watch?v={video_id}"],
                capture_output=True, text=True, timeout=30
            )
            title = result.stdout.strip() or video_id
        except Exception:
            title = video_id
    song = {
        "video_id": video_id, "title": title, "channel": channel or "",
        "source": "youtube", "duration": duration, "skips": 0, "plays": 0
    }
    add(song)
    return song

def add_from_url(url, title=""):
    song = {
        "url": url, "title": title or url, "channel": "",
        "source": "url", "duration": 0, "skips": 0, "plays": 0
    }
    add(song)
    return song

def list_all():
    return load()

def reset_skips(video_id=None, url=None):
    songs = load()
    for s in songs:
        if video_id and s.get("video_id") == video_id:
            s["skips"] = 0
            break
        if url and s.get("url") == url:
            s["skips"] = 0
            break
    save(songs)
    return {"status": "reset", "video_id": video_id, "url": url}

def stats():
    songs = load()
    pool = active_pool(songs)
    removed = [s for s in songs if s.get("skips", 0) >= SKIP_THRESHOLD]
    return {
        "total": len(songs),
        "active": len(pool),
        "removed": len(removed),
        "skip_threshold": SKIP_THRESHOLD,
    }
