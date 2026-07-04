import json
import pickle
from ml.training.feature_engineering import build_embeddings, filter_music
from sklearn.preprocessing import normalize


def train_model(data_path="data/raw/songs.json"):
    with open(data_path, "r") as f:
        songs = json.load(f)
        songs = filter_music(songs)

    print(f"Training on {len(songs)} songs...")
    embeddings = build_embeddings(songs)
    embeddings = normalize(embeddings)

    with open("ml/model.pkl", "wb") as f:
        pickle.dump((songs, embeddings), f)

    print("Model trained and saved!")


if __name__ == "__main__":
    train_model()
