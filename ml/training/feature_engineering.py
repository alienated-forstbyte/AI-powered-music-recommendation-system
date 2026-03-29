from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer


model = SentenceTransformer('all-MiniLM-L6-v2')


def build_embeddings(songs):
    texts = []

    for song in songs:
        text = " ".join([
            song.get("title", ""),
            song.get("channel", "")
        ])
        texts.append(text)

    embeddings = model.encode(texts)

    return embeddings

def build_corpus(songs):
    corpus = []

    for song in songs:
        text = " ".join([
            song.get("title", ""),
            song.get("channel", ""),
            " ".join(song.get("tags", []) if song.get("tags") else [])
        ])

        corpus.append(text.lower())

    return corpus

def is_music(song):
    keywords = ["song", "music", "official", "lyrics", "audio"]
    text = song.get("title", "").lower()

    return any(k in text for k in keywords)

def filter_music(songs):
    return [s for s in songs if is_music(s)]

# songs = [s for s in songs if is_music(s)]


def vectorize(corpus):
    vectorizer = TfidfVectorizer(stop_words="english")
    vectors = vectorizer.fit_transform(corpus)

    return vectorizer, vectors