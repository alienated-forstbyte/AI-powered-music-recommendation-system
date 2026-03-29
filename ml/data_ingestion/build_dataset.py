from collections import defaultdict


def build_user_dataset(plays):
    user_data = defaultdict(list)

    for p in plays:
        user_data[p["user_id"]].append(p["video_id"])

    return dict(user_data)