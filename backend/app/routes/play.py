from fastapi import APIRouter
from backend.app.services.logging_service import log_event
from backend.app.services.user_service import log_user_play

router = APIRouter(prefix="/play", tags=["Play"])


@router.post("/")
def play(video_id: str, user_id: str = "user_1"):
    log_event("play", {
        "user_id": user_id,
        "video_id": video_id
    })

    # 🔥 store locally for ML
    log_user_play(user_id, video_id)

    return {"status": "logged"}