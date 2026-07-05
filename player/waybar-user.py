#!/usr/bin/env python3
"""Waybar custom module for switching between favorite users.

Add to ~/.config/waybar/config.jsonc:
  "custom/music-user": {
    "exec": "python3 /path/to/player/waybar-user.py",
    "on-click": "python3 /path/to/player/ctl.py user user_2",
    "on-click-right": "python3 /path/to/player/ctl.py user user_3",
    "on-click-middle": "python3 /path/to/player/ctl.py user user_4",
    "return-type": "json",
    "interval": 5
  }

  Left click → user_2  |  Right click → user_3  |  Middle click → user_4
Tooltip shows all favorites and which is active.

Add to ~/.config/waybar/style.css:
  #custom-music-user { padding: 0 8px; }
  #custom-music-user.active { color: #e94560; }
  #custom-music-user.other { color: #888; }
"""

import json
import os
import socket
import sys

from player.user_state import get_current_user, FAV_USERS


def waybar_output():
    current = get_current_user()
    stars = "".join("★" if u == current else "☆" for u in FAV_USERS)
    text = f"👤 {current}  {stars}"

    tooltip_lines = [f"Current: {current}", "", "Favorites:"]
    for u in FAV_USERS:
        mark = "▶" if u == current else " "
        tooltip_lines.append(f"  {mark} {u}")
    tooltip_lines.extend([
        "",
        "Left click  → user_2",
        "Right click → user_3",
        "Middle click → user_4",
    ])

    cls = "active" if current in FAV_USERS else "other"

    print(json.dumps({
        "text": text,
        "class": cls,
        "tooltip": "\n".join(tooltip_lines),
    }))


if __name__ == "__main__":
    waybar_output()
