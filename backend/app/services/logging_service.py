import requests
import json
from datetime import datetime

LOKI_URL = "http://localhost:3100/loki/api/v1/push"


def log_event(event_type: str, data: dict):
    """
    Send logs to Loki
    """

    log_entry = {
        "event_type": event_type,
        "timestamp": datetime.utcnow().isoformat(),
        **data
    }

    payload = {
        "streams": [
            {
                "stream": {
                    "app": "music-recommender",
                    "event": event_type
                },
                "values": [
                    [
                        str(int(datetime.utcnow().timestamp() * 1e9)),
                        json.dumps(log_entry)
                    ]
                ]
            }
        ]
    }

    try:
        requests.post(LOKI_URL, json=payload)
    except Exception as e:
        print("Logging failed:", e)