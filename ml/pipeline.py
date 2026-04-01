from data_ingestion.fetch_logs import fetch_logs
from data_ingestion.parse_logs import parse_logs
from data_ingestion.build_dataset import build_user_dataset

from yt_dlp import YoutubeDL

import json
from training.train import train_model


def run_pipeline():
    logs = fetch_logs()
    plays = parse_logs(logs)
    dataset = build_user_dataset(plays)

    print("Users:", len(dataset))

    # 🔥 Save dataset
    with open("data/processed/user_data.json", "w") as f:
        json.dump(dataset, f, indent=2)

    # 🔥 ALSO build song dataset (flatten)
    all_video_ids = set()
    for vids in dataset.values():
        all_video_ids.update(vids)
    print("Collected video IDs:", all_video_ids)

    with open("data/raw/songs.json", "r") as f:
        songs = json.load(f)
    print("All video IDs:", all_video_ids)

    with open("data/raw/songs.json", "w") as f:
        json.dump(songs, f, indent=2)

    # 🔥 Retrain model
    train_model("data/raw/songs.json")

    print("Pipeline complete + model updated")

def fetch_metadata(video_ids):
    ydl_opts = {
        "quiet": True,
        "skip_download": True
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
                    "tags": info.get("tags", [])
                })

            except Exception as e:
                print("Failed:", vid)
                songs.append({
                    "video_id": vid,
                    "title": vid,
                    "channel": "",
                    "tags": []
                })


    return songs

if __name__ == "__main__":
    run_pipeline()