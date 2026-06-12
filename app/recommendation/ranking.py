import math
from typing import List

# Scoring weights (must sum to 1.0)
W_SIMILARITY = 0.5   # FAISS cosine similarity
W_RATING     = 0.3   # product star rating
W_POPULARITY = 0.2   # number of ratings (log-scaled)


def _normalize_rating(rating: float) -> float:
    return max(0.0, min(float(rating), 5.0)) / 5.0


def _normalize_popularity(rating_count: int, max_count: int) -> float:
    if max_count <= 0:
        return 0.0
    log_count = math.log1p(rating_count)
    log_max   = math.log1p(max_count)
    return log_count / log_max if log_max > 0 else 0.0


def rerank(products: List[dict]) -> List[dict]:
    if not products:
        return []

    max_count = max(int(p.get("rating_count", 0)) for p in products)

    for p in products:
        sim   = float(p.get("similarity_score", 0))
        rat   = float(p.get("rating", 0))
        count = int(p.get("rating_count", 0))

        p["final_score"] = round(
            W_SIMILARITY * sim +
            W_RATING     * _normalize_rating(rat) +
            W_POPULARITY * _normalize_popularity(count, max_count),
            4
        )

    ranked = sorted(products, key=lambda x: x["final_score"], reverse=True)
    for i, p in enumerate(ranked, 1):
        p["rank"] = i

    return ranked