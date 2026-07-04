from yt_dlp import YoutubeDL
import json

QUERIES = [
    "arijit singh songs",
    "bollywood hits",
    "lofi music",
    "study lofi beats",
    "english pop songs",
    "top hits 2025",
    "ed sheeran songs",
    "relax music",
]


def fetch_songs(max_results=20):
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
    }

    all_songs = {}

    with YoutubeDL(ydl_opts) as ydl:
        for query in QUERIES:
            search_query = f"ytsearch{max_results}:{query}"
            results = ydl.extract_info(search_query, download=False)

            for entry in results["entries"]:
                vid = entry["id"]

                if vid not in all_songs:
                    all_songs[vid] = {
                        "video_id": vid,
                        "title": entry.get("title", ""),
                        "channel": entry.get("uploader", ""),
                        "tags": entry.get("tags") or [],
                    }

    return list(all_songs.values())


if __name__ == "__main__":
    songs = fetch_songs(20)

    with open("data/raw/songs.json", "w") as f:
        json.dump(songs, f, indent=2)

    print(f"Saved {len(songs)} songs")
