import json
import pickle
from sklearn.metrics.pairwise import cosine_similarity
from training.feature_engineering import build_corpus, vectorize, filter_music
from training.feature_engineering import build_embeddings
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize

def train_model(data_path="data/raw/songs.json"):
    with open(data_path, "r") as f:
        songs = json.load(f)
        songs = filter_music(songs)

    corpus = build_corpus(songs)
    embeddings = build_embeddings(songs)
    embeddings = normalize(embeddings)
    similarity_matrix = cosine_similarity(embeddings)

    with open("ml/model.pkl", "wb") as f:
        pickle.dump((songs, embeddings), f)
        

    print("Model trained and saved!")


if __name__ == "__main__":
    train_model()