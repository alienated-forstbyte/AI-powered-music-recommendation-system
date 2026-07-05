import json
import os
from pathlib import Path

CACHE_DIR = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "music-player"
USER_FILE = CACHE_DIR / "current_user"

def _ensure_cache():
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

def get_current_user():
    _ensure_cache()
    if USER_FILE.exists():
        return USER_FILE.read_text().strip()
    return "user_1"

def set_current_user(user_id: str):
    _ensure_cache()
    USER_FILE.write_text(user_id.strip())

def list_users():
    try:
        import urllib.request
        r = urllib.request.urlopen("http://localhost:8000/users/", timeout=3)
        return json.loads(r.read().decode())
    except Exception:
        return []

def cycle_user():
    users = list_users()
    if not users:
        return get_current_user()
    current = get_current_user()
    if current in users:
        idx = (users.index(current) + 1) % len(users)
    else:
        idx = 0
    next_user = users[idx]
    set_current_user(next_user)
    return next_user

FAV_USERS = ["user_2", "user_3", "user_4"]

def cycle_fav_user():
    current = get_current_user()
    if current in FAV_USERS:
        idx = (FAV_USERS.index(current) + 1) % len(FAV_USERS)
    else:
        idx = 0
    next_user = FAV_USERS[idx]
    set_current_user(next_user)
    return next_user
