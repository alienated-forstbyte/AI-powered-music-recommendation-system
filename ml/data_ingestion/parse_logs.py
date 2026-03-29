import json


def parse_logs(log_lines):
    plays = []

    for line in log_lines:
        try:
            log = json.loads(line)

            if log.get("event_type") == "play":
                plays.append({
                    "user_id": log.get("user_id"),
                    "video_id": log.get("video_id")
                })

        except:
            continue

    return plays