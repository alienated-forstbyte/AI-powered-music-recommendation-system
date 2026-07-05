import sqlite3
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from backend.app.routes import search, recommend, play
from backend.app.routes import feedback
from backend.app.routes import player

app = FastAPI(title="Music Recommender")


@app.get("/users/")
def list_users():
    try:
        db = os.environ.get("USER_DB_PATH", "db/user_history.db")
        conn = sqlite3.connect(db)
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT user_id FROM play_events ORDER BY user_id")
        users = [r[0] for r in cur.fetchall()]
        conn.close()
        return users
    except Exception:
        return []


app.include_router(play.router)
app.include_router(search.router)
app.include_router(recommend.router)
app.include_router(feedback.router)
app.include_router(player.router)

@app.get("/status", response_class=HTMLResponse)
def status_page():
    return Path("backend/app/static/status.html").read_text()


app.mount("/", StaticFiles(directory="backend/app/static", html=True), name="static")
