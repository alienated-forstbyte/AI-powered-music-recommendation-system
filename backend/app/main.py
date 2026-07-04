from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from backend.app.routes import search, recommend, play
from backend.app.routes import feedback
from backend.app.routes import player

app = FastAPI(title="Music Recommender")

app.include_router(play.router)
app.include_router(search.router)
app.include_router(recommend.router)
app.include_router(feedback.router)
app.include_router(player.router)

app.mount("/", StaticFiles(directory="backend/app/static", html=True), name="static")
