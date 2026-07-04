#!/usr/bin/env python3
"""Music player daemon — plays YouTube audio via ffplay, controllable via Unix socket."""

import asyncio
import json
import os
import signal
import subprocess
import tempfile
import threading
from pathlib import Path

SOCKET_PATH = os.environ.get("MUSIC_PLAYER_SOCKET", "/tmp/music-player.sock")
TCP_PORT = os.environ.get("MUSIC_PLAYER_PORT")
if TCP_PORT is not None:
    TCP_PORT = int(TCP_PORT)
CACHE_DIR = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "music-player"
YTLP_PATH = os.environ.get("YTLP_PATH", "yt-dlp")
YTLP_EXTRA = os.environ.get("YTLP_EXTRA", "--js-runtimes deno --cookies-from-browser firefox")
STATE_FILE = CACHE_DIR / "state.json"


class PlayerDaemon:
    def __init__(self):
        self.queue: list[dict] = []
        self.current_index: int | None = None
        self.ffplay_proc: subprocess.Popen | None = None
        self.paused = False
        self.volume = 100
        self.current_song: dict | None = None
        self._ffplay_ended = threading.Event()
        self._skip_lock = threading.Lock()
        self._last_skip_at = 0.0

        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        self._load_state()

    # ── socket handling ──────────────────────────────────────────

    async def _handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        try:
            data = b""
            while True:
                chunk = await reader.read(4096)
                if not chunk:
                    break
                data += chunk
                if len(chunk) < 4096:
                    break
            raw = data.decode().strip()
            result = self._dispatch(raw)
            writer.write(result.encode() + b"\n")
            await writer.drain()
        except (ConnectionResetError, BrokenPipeError, OSError):
            pass
        finally:
            try:
                writer.close()
            except Exception:
                pass

    def _dispatch(self, raw: str) -> str:
        try:
            msg = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            return json.dumps({"error": "invalid JSON"})
        cmd = msg.get("command", "")
        args = msg.get("args", {})

        handlers = {
            "play": lambda: self._cmd_play(args.get("video_id"), args.get("title", ""), args.get("channel", "")),
            "pause": self._cmd_pause,
            "toggle": self._cmd_toggle,
            "next": self._cmd_next,
            "prev": self._cmd_prev,
            "stop": self._cmd_stop,
            "volume": lambda: self._cmd_volume(args.get("level")),
            "queue": self._cmd_queue,
            "add": lambda: self._cmd_add(args.get("video_id"), args.get("title", ""), args.get("channel", "")),
            "remove": lambda: self._cmd_remove(args.get("index")),
            "clear": self._cmd_clear,
            "status": self._cmd_status,
            "list_playlists": self._cmd_list_playlists,
            "load_playlist": lambda: self._cmd_load_playlist(args.get("name")),
            "save_playlist": lambda: self._cmd_save_playlist(args.get("name")),
        }
        handler = handlers.get(cmd)
        if handler is None:
            return json.dumps({"error": f"unknown command: {cmd}"})
        try:
            return json.dumps(handler())
        except Exception as e:
            return json.dumps({"error": str(e)})

    # ── playback ─────────────────────────────────────────────────

    def _get_audio_url(self, video_id: str) -> str | None:
        try:
            cmd = [YTLP_PATH] + YTLP_EXTRA.split() + ["-f", "bestaudio", "--get-url", f"https://youtube.com/watch?v={video_id}"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, env={**os.environ, "PATH": os.environ.get("PATH", "")})
            url = result.stdout.strip()
            return url if url else None
        except Exception as e:
            self._log(f"yt-dlp error for {video_id}: {e}")
            return None

    def _play_index(self, index: int):
        if not self.queue or index < 0 or index >= len(self.queue):
            self.current_index = None
            self.current_song = None
            self._stop_ffplay()
            self._save_state()
            return

        self.current_index = index
        self._do_play()

    def _do_play(self):
        if self.current_index is None:
            return
        song = self.queue[self.current_index]
        self.current_song = song
        self._save_state()

        url = self._get_audio_url(song["video_id"])
        if not url:
            self._log(f"Can't get audio URL for {song['video_id']}, skipping")
            threading.Thread(target=self._skip_after_cooldown, daemon=True).start()
            return

        self._stop_ffplay()
        self.paused = False
        self._ffplay_ended.clear()

        self.ffplay_proc = subprocess.Popen(
            ["ffplay", "-nodisp", "-autoexit", "-volume", str(self.volume), url],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            preexec_fn=os.setsid,
        )
        self._log(f"Playing: {song.get('title', song['video_id'])}")

        threading.Thread(target=self._wait_ffplay, daemon=True).start()

    def _skip_after_cooldown(self):
        import time
        time.sleep(3)
        self._cmd_next()

    def _wait_ffplay(self):
        proc = self.ffplay_proc
        if proc:
            proc.wait()
            self._ffplay_ended.set()
            # Only auto-advance if ffplay exited cleanly (song finished naturally),
            # not if it failed (e.g. expired URL, network error)
            if proc.returncode == 0 and not self.paused and self.current_index is not None:
                if len(self.queue) > 1:
                    self._log("Song finished, advancing to next")
                    self._cmd_next()
                else:
                    self._log("Song finished, end of queue")
                    self._cmd_stop()

    def _stop_ffplay(self):
        if self.ffplay_proc:
            try:
                os.killpg(os.getpgid(self.ffplay_proc.pid), signal.SIGTERM)
            except (ProcessLookupError, PermissionError):
                pass
            try:
                self.ffplay_proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                try:
                    self.ffplay_proc.kill()
                except Exception:
                    pass
            self.ffplay_proc = None

    # ── commands ──────────────────────────────────────────────────

    def _cmd_play(self, video_id, title="", channel=""):
        self._cmd_add(video_id, title, channel)
        self._play_index(len(self.queue) - 1)
        return {"status": "playing", "song": self.current_song}

    def _cmd_pause(self):
        if self.ffplay_proc is None:
            return {"status": "no_active_playback"}
        try:
            os.killpg(os.getpgid(self.ffplay_proc.pid), signal.SIGSTOP)
        except ProcessLookupError:
            return {"status": "no_active_playback"}
        self.paused = True
        return {"status": "paused"}

    def _cmd_toggle(self):
        if self.paused:
            return self._cmd_resume()
        else:
            return self._cmd_pause()

    def _cmd_resume(self):
        if self.ffplay_proc is None:
            return {"status": "no_active_playback"}
        try:
            os.killpg(os.getpgid(self.ffplay_proc.pid), signal.SIGCONT)
        except ProcessLookupError:
            return {"status": "no_active_playback"}
        self.paused = False
        return {"status": "resumed"}

    def _cmd_next(self):
        if not self.queue:
            return {"status": "empty_queue"}
        with self._skip_lock:
            now = __import__('time').time()
            if now - self._last_skip_at < 2.0:
                return {"status": "debounced"}
            self._last_skip_at = now
        nxt = 0 if self.current_index is None else (self.current_index + 1) % len(self.queue)
        self._play_index(nxt)
        return {"status": "playing", "song": self.current_song}

    def _cmd_prev(self):
        if not self.queue:
            return {"status": "empty_queue"}
        with self._skip_lock:
            now = __import__('time').time()
            if now - self._last_skip_at < 2.0:
                return {"status": "debounced"}
            self._last_skip_at = now
        prv = len(self.queue) - 1 if self.current_index is None else (self.current_index - 1) % len(self.queue)
        self._play_index(prv)
        return {"status": "playing", "song": self.current_song}

    def _cmd_stop(self):
        self._stop_ffplay()
        self.current_index = None
        self.current_song = None
        self.paused = False
        self._save_state()
        return {"status": "stopped"}

    def _cmd_volume(self, level):
        if level is not None:
            self.volume = max(0, min(150, int(level)))
        return {"status": "ok", "volume": self.volume}

    def _cmd_queue(self):
        return {"queue": self.queue, "current_index": self.current_index}

    def _cmd_add(self, video_id, title="", channel=""):
        song = {"video_id": video_id, "title": title or video_id, "channel": channel}
        self.queue.append(song)
        if self.current_index is None and self.queue:
            self.current_index = 0
        self._save_state()
        return {"status": "added", "index": len(self.queue) - 1}

    def _cmd_remove(self, index):
        if index is None or index < 0 or index >= len(self.queue):
            return {"error": "invalid index"}
        self.queue.pop(index)
        if self.current_index is not None:
            if index < self.current_index:
                self.current_index -= 1
            elif index == self.current_index:
                if self.queue:
                    self.current_index = min(self.current_index, len(self.queue) - 1)
                    self._do_play()
                else:
                    self._cmd_stop()
        self._save_state()
        return {"status": "removed"}

    def _cmd_clear(self):
        self._stop_ffplay()
        self.queue.clear()
        self.current_index = None
        self.current_song = None
        self.paused = False
        self._save_state()
        return {"status": "cleared"}

    def _cmd_status(self):
        status_str = "stopped"
        if self.ffplay_proc is not None:
            status_str = "paused" if self.paused else "playing"

        return {
            "status": status_str,
            "song": self.current_song,
            "queue_length": len(self.queue),
            "current_index": self.current_index,
            "volume": self.volume,
        }

    # ── playlists ────────────────────────────────────────────────

    def _playlists_dir(self):
        d = CACHE_DIR / "playlists"
        d.mkdir(parents=True, exist_ok=True)
        return d

    def _cmd_list_playlists(self):
        files = sorted(self._playlists_dir().glob("*.json"))
        return {"playlists": [f.stem for f in files]}

    def _cmd_save_playlist(self, name):
        if not name:
            return {"error": "name required"}
        path = self._playlists_dir() / f"{name}.json"
        with open(path, "w") as f:
            json.dump({"songs": self.queue}, f, indent=2)
        return {"status": "saved", "name": name, "count": len(self.queue)}

    def _cmd_load_playlist(self, name):
        if not name:
            return {"error": "name required"}
        path = self._playlists_dir() / f"{name}.json"
        if not path.exists():
            return {"error": f"playlist '{name}' not found"}
        with open(path) as f:
            data = json.load(f)
        self.queue = data.get("songs", [])
        self.current_index = 0 if self.queue else None
        self._do_play()
        return {"status": "loaded", "name": name, "count": len(self.queue)}

    # ── persistence ──────────────────────────────────────────────

    def _save_state(self):
        try:
            data = {
                "queue": self.queue,
                "current_index": self.current_index,
                "volume": self.volume,
            }
            with tempfile.NamedTemporaryFile(mode="w", dir=CACHE_DIR, delete=False) as f:
                json.dump(data, f)
                tmp = f.name
            os.replace(tmp, STATE_FILE)
        except Exception as e:
            self._log(f"save error: {e}")

    def _load_state(self):
        try:
            if STATE_FILE.exists():
                with open(STATE_FILE) as f:
                    data = json.load(f)
                self.queue = data.get("queue", [])
                self.current_index = data.get("current_index")
                self.volume = data.get("volume", 100)
        except Exception as e:
            self._log(f"load error: {e}")

    # ── lifecycle ────────────────────────────────────────────────

    def _log(self, msg):
        print(f"[player] {msg}", flush=True)

    async def run(self):
        servers = []

        # Unix socket
        if os.path.exists(SOCKET_PATH):
            os.unlink(SOCKET_PATH)
        us = await asyncio.start_unix_server(self._handle_client, path=SOCKET_PATH)
        os.chmod(SOCKET_PATH, 0o666)
        servers.append(us)
        self._log(f"Unix socket: {SOCKET_PATH}")

        # Optional TCP (for Docker/host bridge)
        if TCP_PORT:
            ts = await asyncio.start_server(self._handle_client, host="0.0.0.0", port=TCP_PORT)
            servers.append(ts)
            self._log(f"TCP port: {TCP_PORT}")

        self._log(f"Queue: {len(self.queue)} songs" + (f", index {self.current_index}" if self.current_index is not None else ""))

        if self.current_index is not None and self.queue:
            self._do_play()

        async with asyncio.TaskGroup() as tg:
            for s in servers:
                tg.create_task(s.serve_forever())


if __name__ == "__main__":
    try:
        asyncio.run(PlayerDaemon().run())
    except KeyboardInterrupt:
        print("[player] Shutting down")
