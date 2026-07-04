from fastapi import APIRouter
from backend.app.services import player_service

router = APIRouter(prefix="/player", tags=["Player"])


@router.post("/play")
def play(video_id: str, title: str = "", channel: str = ""):
    return player_service.play(video_id, title=title, channel=channel)


@router.post("/play_index")
def play_index(index: int):
    return player_service.play_index(index)


@router.post("/add")
def add(video_id: str, title: str = "", channel: str = ""):
    return player_service.add(video_id, title=title, channel=channel)


@router.post("/pause")
def pause():
    return player_service.pause()


@router.post("/toggle")
def toggle():
    return player_service.toggle()


@router.post("/next")
def next_track():
    return player_service.next_track()


@router.post("/prev")
def prev_track():
    return player_service.prev_track()


@router.post("/stop")
def stop():
    return player_service.stop()


@router.post("/volume")
def set_volume(level: int | None = None):
    return player_service.volume(level)


@router.get("/status")
def get_status():
    return player_service.status()


@router.get("/queue")
def get_queue():
    return player_service.queue()


@router.post("/remove")
def remove(index: int):
    return player_service.remove(index)


@router.post("/clear")
def clear():
    return player_service.clear()


@router.post("/save")
def save(name: str):
    return player_service.save_playlist(name)


@router.post("/load")
def load(name: str):
    return player_service.load_playlist(name)


@router.get("/playlists")
def list_playlists():
    return player_service.list_playlists()
