# Music Player AI — API

Base URL

http://localhost:8000

---

## Search

GET /search/

Parameters

- query — search string
- max_results — max results (default 5)

Returns

Array of YouTube video results.

---

## Play (Log Only)

POST /play/

Parameters

- video_id — YouTube video ID
- user_id — user identifier (default user_1)

Returns

```
{ "status": "logged" }
```

---

## Recommend

GET /recommend/user

Parameters

- user_id — user identifier
- top_k — number of recommendations (default 5)

Returns

Array of song objects sorted by relevance.

---

POST /recommend/reload

Reloads ML model from disk.

Returns

```
{ "status": "model reloaded" }
```

---

## Feedback

POST /feedback/

Parameters

- user_id — user identifier
- video_id — YouTube video ID
- action — skip | dislike
- tags — comma-separated tag string (optional)

Returns

```
{ "status": "logged", "excluded_tags": [...], "skip_limit": 3 }
```

---

## Player Daemon (Proxy)

All endpoints prefixed with /player/

### POST /player/play

Start playing a song (adds to queue and plays).

Parameters

- video_id — YouTube video ID or URL
- title — display title (optional)
- channel — channel name (optional)

Returns

```
{ "status": "playing", "song": { ... } }
```

### POST /player/play_index

Play song at queue index.

Parameters

- index — queue position (integer)

Returns

```
{ "status": "playing", "song": { ... } }
```

### POST /player/add

Add song to end of queue.

Parameters

- video_id — YouTube video ID or URL
- title — display title (optional)
- channel — channel name (optional)

Returns

```
{ "status": "added", "index": 0 }
```

### POST /player/pause

Toggle pause.

Returns

```
{ "status": "paused" }
```

### POST /player/toggle

Play / pause toggle.

Returns

```
{ "status": "paused" | "resumed" }
```

### POST /player/next

Next track.

Returns

```
{ "status": "next", "song": { ... } }
```

### POST /player/prev

Previous track.

Returns

```
{ "status": "prev", "song": { ... } }
```

### POST /player/stop

Stop playback.

Returns

```
{ "status": "stopped" }
```

### POST /player/volume

Set or get volume.

Parameters

- level — volume 0-150 (optional; if omitted returns current)

Returns

```
{ "status": "ok", "volume": 80 }
```

### GET /player/status

Current daemon state.

Returns

```
{ "status": "playing", "song": {...}, "queue_length": 3, "current_index": 0, "volume": 100 }
```

### GET /player/queue

Full queue list.

Returns

```
{ "queue": [...], "current_index": 0 }
```

### POST /player/remove

Remove song from queue.

Parameters

- index — queue position

Returns

```
{ "status": "removed" }
```

### POST /player/clear

Clear entire queue.

Returns

```
{ "status": "cleared" }
```

### POST /player/save

Save current queue as named playlist.

Parameters

- name — playlist name

Returns

```
{ "status": "saved", "name": "mymix" }
```

### POST /player/load

Load a saved playlist into queue.

Parameters

- name — playlist name

Returns

```
{ "status": "loaded", "name": "mymix", "count": 5 }
```

### GET /player/playlists

List saved playlists.

Returns

```
["mymix", "chill", "focus"]
```

---

## Error Responses

All endpoints return JSON.

Errors return:

```
{ "error": "description", "hint": "suggestion" }
```

HTTP status codes:

- 200 — success
- 503 — model not loaded / daemon not running
