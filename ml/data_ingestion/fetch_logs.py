import requests
# import time

# LOKI_QUERY_URL = "http://localhost:3100/loki/api/v1/query_range"


# def fetch_logs():
#     query = '{app="music-recommender"}'

#     now = int(time.time() * 1e9)
#     one_hour_ago = now - (60 * 60 * 1e9)

    # import requests
import time

LOKI_QUERY_URL = "http://localhost:3100/loki/api/v1/query_range"


def fetch_logs():
    query = '{app="music-recommender"}'

    now = time.time_ns()
    ten_minutes_ago = now - (10 * 60 * 1_000_000_000)
    one_day_ago = now - (24 * 60 * 60 * 1_000_000_000)

    params = {
        "query": query,
        "limit": 1000,
        "start": str(one_day_ago),
        "end": str(now)
    }

    response = requests.get(LOKI_QUERY_URL, params=params)
    data = response.json()

    logs = []

    for stream in data.get("data", {}).get("result", []):
        for value in stream.get("values", []):
            log_line = value[1]
            logs.append(log_line)

    print("RAW LOGS:", logs[:3])  # debug

    return logs