from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')


def build_text(song):
    parts = [song.get("title", ""), song.get("channel", "")]
    tags = song.get("tags", [])
    if tags:
        parts.append(" ".join(tags))
    return " ".join(parts)


def build_embeddings(songs):
    texts = [build_text(s) for s in songs]
    return model.encode(texts)


def build_corpus(songs):
    return [build_text(s).lower() for s in songs]


def filter_music(songs):
    non_music_keywords = [
        "podcast", "episode", "interview", "tutorial", "lecture",
        "news", "debate", "documentary", "review", "trailer",
        "gameplay", "walkthrough", "stream", "vlog",
    ]
    filtered = []
    for s in songs:
        text = (s.get("title", "") + " " + s.get("channel", "")).lower()
        if any(k in text for k in non_music_keywords):
            continue
        filtered.append(s)
    return filtered
