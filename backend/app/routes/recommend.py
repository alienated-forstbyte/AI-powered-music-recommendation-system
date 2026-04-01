from fastapi import APIRouter
from ml.inference.recommender import Recommender
from backend.app.services.user_service import get_user_history

router = APIRouter(prefix="/recommend", tags=["Recommend"])

model = Recommender()

@router.post("/reload")
def reload_model():
    global model
    model = Recommender()
    return {"status": "model reloaded"}

@router.get("/user")
def recommend_user(user_id: str):
    model = Recommender()
    history = get_user_history(user_id)
    return model.recommend_for_user(history)