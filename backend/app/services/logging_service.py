import requests
import json
from datetime import datetime
import time

LOKI_URL = "http://localhost:3100/loki/api/v1/push"


def log_event(event_type: str, data: dict):
    """
    Send logs to Loki
    """
    print("LOGGING EVENT:", event_type, data)
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
                        str(time.time_ns()),
                        json.dumps(log_entry)
                    ],
                ]
            }
        ]
    }

    try:
        response = requests.post(
        LOKI_URL,
        data=json.dumps(payload),
        headers={"Content-Type": "application/json"}
    )
        print("Loki response:", response.status_code, response.text)

    except Exception as e:
        print("Logging failed:", e)