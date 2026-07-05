#!/usr/bin/env bash
set -e
export PATH="$HOME/.deno/bin:$PATH"
export MUSIC_PLAYER_PORT=18765
cd /mnt/new-volume/MLOps/Music\ Player\ AI
rm -f /tmp/music-player.sock
MODE=""
if [ "${1:-}" = "--collection" ]; then
  MODE="--collection"
fi
exec python3 -m player.daemon $MODE
