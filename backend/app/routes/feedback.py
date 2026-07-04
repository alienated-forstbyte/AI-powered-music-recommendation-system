from fastapi import APIRouter
from backend.app.services.user_service import get_excluded_tags, SKIP_LIMIT
from backend.app.services.feedback_service import process_feedback

router = APIRouter(prefix="/feedback", tags=["Feedback"])


@router.post("/")
def feedback(user_id: str, video_id: str, action: str, tags: str = ""):
    song_tags = [t.strip() for t in tags.split(",") if t.strip()] if tags else []
    process_feedback(user_id, video_id, action, song_tags)
    excluded = get_excluded_tags(user_id)
    return {
        "status": "logged",
        "excluded_tags": list(excluded),
        "skip_limit": SKIP_LIMIT,
    }
