# Temporary in-memory store (later → Loki)
USER_HISTORY = {}


def log_user_play(user_id: str, video_id: str):
    if user_id not in USER_HISTORY:
        USER_HISTORY[user_id] = []

    USER_HISTORY[user_id].append(video_id)


def get_user_history(user_id: str):
    return USER_HISTORY.get(user_id, [])