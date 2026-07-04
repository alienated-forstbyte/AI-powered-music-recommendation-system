import pickle
from collections import Counter
import numpy as np


class Recommender:
    def __init__(self, model_path="ml/model.pkl"):
        with open(model_path, "rb") as f:
            self.songs, self.embeddings = pickle.load(f)

        self.video_to_index = {
            song["video_id"]: i for i, song in enumerate(self.songs)
        }

    def recommend_for_user(self, user_history, top_k=5, excluded_tags=None):
        excluded_tags = excluded_tags or set()
        vectors = []

        for vid in user_history:
            if vid in self.video_to_index:
                idx = self.video_to_index[vid]
                vectors.append(self.embeddings[idx])

        if not vectors:
            available = self._filter_excluded(self.songs, excluded_tags)
            return available[:top_k]

        user_vector = np.mean(vectors, axis=0)
        user_vector = user_vector / np.linalg.norm(user_vector)

        scores = []
        for i, song_vec in enumerate(self.embeddings):
            score = np.dot(user_vector, song_vec)
            scores.append((i, score))

        ranked = sorted(scores, key=lambda x: x[1], reverse=True)

        recommendations = []
        for i, _ in ranked:
            song = self.songs[i]
            if song["video_id"] in user_history:
                continue
            if self._has_excluded_tag(song, excluded_tags):
                continue
            recommendations.append(song)
            if len(recommendations) >= top_k:
                break

        return recommendations

    def _has_excluded_tag(self, song, excluded_tags):
        if not excluded_tags:
            return False
        song_tags = song.get("tags", []) or []
        for tag in song_tags:
            words = tag.lower().split()
            if any(excluded in words for excluded in excluded_tags):
                return True
        return False

    def _filter_excluded(self, songs, excluded_tags):
        if not excluded_tags:
            return songs
        return [s for s in songs if not self._has_excluded_tag(s, excluded_tags)]
