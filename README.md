# Music Player AI

A music recommendation system that uses YouTube as its music source with NLP-powered content-based filtering. Built with FastAPI, sentence-transformers, and the Grafana observability stack.

## Architecture

```
User → FastAPI Backend (port 8000)
         ├── /search/   → yt-dlp (YouTube search, no API key needed)
         ├── /play/     → SQLite (user history) + Loki (log aggregation)
         └── /recommend/ → sentence-transformers embeddings + cosine similarity
```

- **Backend**: FastAPI + Uvicorn
- **Storage**: SQLite (user play history) + JSON files (song catalog)
- **ML**: sentence-transformers (`all-MiniLM-L6-v2`) → 384-dim embeddings → cosine similarity
- **Observability**: Grafana Loki (logs) + Grafana (dashboard at port 3000)
- **YouTube**: yt-dlp (no API key required)

## Quick Start

```bash
# Start all services
make up

# Seed the song catalog (first time only)
python -m ml.data_ingestion.fetch_songs

# Train the recommendation model
make train

# Test the API endpoints
make test
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Health check |
| GET | `/search/?query=<q>&max_results=<n>` | Search YouTube |
| POST | `/play/?video_id=<id>&user_id=<id>` | Log a play event |
| GET | `/recommend/user?user_id=<id>&top_k=<n>` | Get recommendations |
| POST | `/recommend/reload` | Reload ML model from disk |

## Project Layout

```
├── backend/              # FastAPI application
│   ├── app/
│   │   ├── main.py
│   │   ├── routes/       # search, play, recommend
│   │   └── services/     # youtube, logging, user (SQLite)
│   └── requirements.txt
├── ml/                   # ML training & inference
│   ├── pipeline.py       # Full training pipeline entrypoint
│   ├── data_ingestion/   # Fetch logs, parse, build dataset
│   ├── training/         # feature_engineering, train (sentence-transformers)
│   ├── inference/        # Recommender class (loads model.pkl)
│   └── requirements.txt
├── data/
│   ├── raw/songs.json    # Song catalog from YouTube
│   └── processed/        # User play history dataset
├── observability/        # Grafana dashboards & Loki datasource
├── docker-compose.yaml   # backend + loki + grafana
└── Makefile
```

## Data Flow

1. User searches YouTube → results returned via yt-dlp
2. User plays a song → play event logged to SQLite + Loki
3. Pipeline reads play history (SQLite → Loki fallback), enriches song catalog with new video metadata, retrains embeddings
4. Recommendations: mean of user's song embeddings → cosine similarity with all songs → top-K unseen

## Training

```bash
make train   # reads SQLite → builds dataset → fetches new song metadata → retrains model
```

## Observability

- Grafana: http://localhost:3000 (admin/admin)
- Loki: http://localhost:3100
- Pre-built dashboard with search events, play events, play count per user, event count by type
