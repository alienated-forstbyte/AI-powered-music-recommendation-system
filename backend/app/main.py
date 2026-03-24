from fastapi import FastAPI
from backend.app.routes import search, recommend

app = FastAPI(title="Music Recommender")

app.include_router(search.router)
app.include_router(recommend.router)

@app.get("/")
def root():
    return {"message": "Music Recommender API running"}