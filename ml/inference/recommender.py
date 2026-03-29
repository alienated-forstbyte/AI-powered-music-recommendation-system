import pickle
from collections import Counter
import numpy as np

class Recommender:
    def __init__(self, model_path="ml/model.pkl"):
        with open(model_path, "rb") as f:
            self.songs, self.similarity_matrix = pickle.load(f)

        # map video_id → index
        self.video_to_index = {
            song["video_id"]: i for i, song in enumerate(self.songs)
        }

    # def recommend_for_user(self, user_history, top_k=5):

    #     video_counts = Counter(user_history)

    #     indices = []
    #     weights = []

    #     for vid, count in video_counts.items():
    #         if vid in self.video_to_index:
    #             indices.append(self.video_to_index[vid])
    #             weights.append(count)

    #     if not indices:
    #         return self.songs[:top_k]

    #     # 🔥 aggregate similarity
    #     scores = [0] * len(self.songs)

    #     for idx, weight in zip(indices, weights):
    #         sim_scores = self.similarity_matrix[idx]
    #         for i in range(len(scores)):
    #             scores[i] += sim_scores[i] * weight

    #     ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)
    #     print("User history:", user_history)
    #     print("Available IDs:", list(self.video_to_index.keys())[:5])

    #     recommendations = []
    #     for i, _ in ranked:
    #         if i not in indices and scores[i] > 0.2:
    #             recommendations.append(self.songs[i])

    #         if len(recommendations) >= top_k:
    #             break

    #     return recommendations
        
    def recommend_for_user(self, user_history, top_k=5):
        vectors = []

        for vid in user_history:
            if vid in self.video_to_index:
                idx = self.video_to_index[vid]
                vectors.append(self.embeddings[idx])

        if not vectors:
            return self.songs[:top_k]

        # 🔥 Create USER VECTOR
        user_vector = np.mean(vectors, axis=0)

        # 🔥 Compare with ALL songs
        scores = []

        for i, song_vec in enumerate(self.embeddings):
            score = np.dot(user_vector, song_vec) / (
                np.linalg.norm(user_vector) * np.linalg.norm(song_vec)
            )
            scores.append((i, score))

        ranked = sorted(scores, key=lambda x: x[1], reverse=True)

        recommendations = []
        for i, _ in ranked:
            if self.songs[i]["video_id"] not in user_history:
                recommendations.append(self.songs[i])

            if len(recommendations) >= top_k:
                break

        return recommendations