import json
import sys
import os

# allow backend imports when running as script
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ml.data_ingestion.fetch_logs import fetch_logs
from ml.data_ingestion.parse_logs import parse_logs
from ml.data_ingestion.build_dataset import build_user_dataset
from ml.training.train import train_model
from yt_dlp import YoutubeDL


def run_pipeline():
    # 1. Try SQLite first (primary source of truth)
    try:
        from backend.app.services.user_service import get_all_play_events
        plays_data = get_all_play_events()
        plays = [
            {"user_id": p["user_id"], "video_id": p["video_id"]}
            for p in plays_data
        ]
        print(f"Loaded {len(plays)} play events from SQLite")
    except Exception as e:
        print(f"SQLite read failed ({e}), falling back to Loki...")
        logs = fetch_logs()
        plays = parse_logs(logs)
        print(f"Loaded {len(plays)} play events from Loki")

    # 2. Build user dataset
    dataset = build_user_dataset(plays)
    print(f"Users in dataset: {len(dataset)}")

    # 3. Save dataset
    os.makedirs("data/processed", exist_ok=True)
    with open("data/processed/user_data.json", "w") as f:
        json.dump(dataset, f, indent=2)

    # 4. Collect all video IDs from play history
    all_video_ids = set()
    for vids in dataset.values():
        all_video_ids.update(vids)
    print(f"Unique video IDs from history: {len(all_video_ids)}")

    # 5. Load existing song catalog
    existing_songs = {}
    if os.path.exists("data/raw/songs.json"):
        with open("data/raw/songs.json", "r") as f:
            for s in json.load(f):
                existing_songs[s["video_id"]] = s

    # 6. Fetch metadata for new video IDs not yet in catalog
    unknown_ids = all_video_ids - set(existing_songs.keys())
    if unknown_ids:
        print(f"Fetching metadata for {len(unknown_ids)} new songs...")
        new_songs = fetch_metadata(list(unknown_ids))
        for s in new_songs:
            existing_songs[s["video_id"]] = s
    else:
        print("No new songs to fetch")

    # 7. Save enriched catalog
    with open("data/raw/songs.json", "w") as f:
        json.dump(list(existing_songs.values()), f, indent=2)
    print(f"Song catalog now has {len(existing_songs)} entries")

    # 8. Retrain model
    train_model("data/raw/songs.json")
    print("Pipeline complete + model updated")


def fetch_metadata(video_ids):
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
    }
    songs = []
    with YoutubeDL(ydl_opts) as ydl:
        for vid in video_ids:
            try:
                url = f"https://www.youtube.com/watch?v={vid}"
                info = ydl.extract_info(url, download=False)
                songs.append({
                    "video_id": vid,
                    "title": info.get("title", ""),
                    "channel": info.get("uploader", ""),
                    "tags": info.get("tags", []),
                })
            except Exception as e:
                print(f"Failed to fetch metadata for {vid}: {e}")
                songs.append({
                    "video_id": vid,
                    "title": vid,
                    "channel": "",
                    "tags": [],
                })
    return songs


if __name__ == "__main__":
    run_pipeline()
