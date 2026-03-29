from fastapi import APIRouter
from ml.inference.recommender import Recommender
from backend.app.services.user_service import get_user_history

router = APIRouter(prefix="/recommend", tags=["Recommend"])

model = Recommender()


@router.get("/user")
def recommend_user(user_id: str):
    history = get_user_history(user_id)
    return model.recommend_for_user(history)