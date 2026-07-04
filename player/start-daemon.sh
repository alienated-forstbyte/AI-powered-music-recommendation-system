#!/usr/bin/env bash
set -e
export PATH="$HOME/.deno/bin:$PATH"
export MUSIC_PLAYER_PORT=18765
cd /mnt/new-volume/MLOps/Music\ Player\ AI
rm -f /tmp/music-player.sock
exec python3 -m player.daemon
