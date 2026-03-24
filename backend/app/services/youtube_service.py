import yt_dlp


def search_youtube(query: str, max_results: int = 10):
    """
    Search YouTube using yt-dlp (no API key required)

    Args:
        query (str): Search query
        max_results (int): Number of results

    Returns:
        list[dict]: List of song metadata
    """

    ydl_opts = {
        "quiet": True,
        "extract_flat": True,   # faster, no full video fetch
        "skip_download": True
    }

    search_query = f"ytsearch{max_results}:{query}"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            results = ydl.extract_info(search_query, download=False)

        songs = []
        for entry in results.get("entries", []):
            songs.append({
                "title": entry.get("title"),
                "video_id": entry.get("id"),
                "url": f"https://www.youtube.com/watch?v={entry.get('id')}",
                "channel": entry.get("uploader"),
                "duration": entry.get("duration"),
                "view_count": entry.get("view_count"),
            })

        return songs

    except Exception as e:
        return {"error": str(e)}


def get_video_details(video_id: str):
    """
    Fetch detailed metadata for a single video
    (useful later for ML features)

    Args:
        video_id (str): YouTube video ID

    Returns:
        dict: Video metadata
    """

    ydl_opts = {
        "quiet": True,
        "skip_download": True
    }

    url = f"https://www.youtube.com/watch?v={video_id}"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        return {
            "title": info.get("title"),
            "video_id": video_id,
            "channel": info.get("uploader"),
            "duration": info.get("duration"),
            "view_count": info.get("view_count"),
            "like_count": info.get("like_count"),
            "tags": info.get("tags"),
            "description": info.get("description"),
        }

    except Exception as e:
        return {"error": str(e)}