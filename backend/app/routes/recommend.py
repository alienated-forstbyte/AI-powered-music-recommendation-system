from fastapi import APIRouter

router = APIRouter(prefix="/recommend", tags=["Recommend"])

@router.get("/")
def recommend():
    return {"message": "Recommendation endpoint coming soon"}