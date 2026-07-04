from fastapi import APIRouter, HTTPException
from ml.inference.recommender import Recommender
from backend.app.services.user_service import get_user_history, get_excluded_tags

router = APIRouter(prefix="/recommend", tags=["Recommend"])

_model = None


def get_model():
    global _model
    if _model is None:
        _model = Recommender()
    return _model


@router.post("/reload")
def reload_model():
    global _model
    _model = Recommender()
    return {"status": "model reloaded"}


@router.get("/user")
def recommend_user(user_id: str, top_k: int = 5):
    try:
        model = get_model()
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Model not loaded: {e}. Train it first with: python -m ml.pipeline",
        )
    history = get_user_history(user_id)
    excluded = get_excluded_tags(user_id)
    return model.recommend_for_user(
        history, top_k=top_k, excluded_tags=excluded
    )
