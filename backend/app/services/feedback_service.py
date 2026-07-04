from backend.app.services.user_service import increment_tag_skips


def process_feedback(user_id: str, video_id: str, action: str, song_tags: list = None):
    if action == "skip":
        if song_tags:
            increment_tag_skips(user_id, song_tags)
