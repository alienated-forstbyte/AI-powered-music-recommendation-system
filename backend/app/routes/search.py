from fastapi import APIRouter
from backend.app.services.youtube_service import search_youtube
from backend.app.services.logging_service import log_event

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("/")
def search(query: str, max_results: int = 5):
    results = search_youtube(query, max_results)

    log_event("search", {
        "query": query,
        "results_count": len(results) if isinstance(results, list) else 0
    })

    return results