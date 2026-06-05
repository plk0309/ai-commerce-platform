import faiss
import numpy as np
import os
from sentence_transformers import SentenceTransformer
from app.recommendation.embeddings import generate_embeddings

# ─── Config ───────────────────────────────────────────────
MODEL_NAME = "all-MiniLM-L6-v2"
FAISS_PATH = "artifacts/faiss_index.bin"
# ──────────────────────────────────────────────────────────

# Global objects (loaded once at startup)
_model = None
_index = None
_products = None


def build_faiss_index(embeddings: np.ndarray) -> faiss.IndexFlatIP:
    """
    Build FAISS cosine similarity index.
    """
    dim = embeddings.shape[1]

    index = faiss.IndexFlatIP(dim)
    index.add(embeddings.astype("float32"))

    faiss.write_index(index, FAISS_PATH)

    print(f"✅ FAISS index built with {index.ntotal} vectors")
    return index


def load_search_engine():
    """
    Loads model, embeddings, FAISS index and products dataframe.
    Runs only once during application startup.
    """
    global _model, _index, _products

    if _model is not None:
        return

    print("🚀 Initializing Search Engine...")

    # Load embeddings + products
    embeddings, _products = generate_embeddings()

    # Load or build FAISS
    if os.path.exists(FAISS_PATH):
        print("⚡ Loading existing FAISS index...")
        _index = faiss.read_index(FAISS_PATH)
    else:
        print("🔨 Building FAISS index...")
        _index = build_faiss_index(embeddings)

    # Load embedding model
    print("🤖 Loading embedding model...")
    _model = SentenceTransformer(MODEL_NAME)

    print("✅ Search Engine ready!")


def search_products(
    query: str,
    top_k: int = 5,
    min_rating: float = 0.0,
    max_price: float = None,
    category_filter: str = None,
) -> list:
    """
    Semantic product search with filters.

    Args:
        query: Search query
        top_k: Number of results
        min_rating: Minimum product rating
        max_price: Maximum discounted price
        category_filter: Category keyword filter

    Returns:
        List of matching products
    """

    load_search_engine()

    query_vec = _model.encode(
        [query],
        normalize_embeddings=True,
        convert_to_numpy=True,
    ).astype("float32")

    fetch_k = min(top_k * 10, len(_products))

    scores, indices = _index.search(query_vec, fetch_k)

    results = []

    for score, idx in zip(scores[0], indices[0]):

        if idx == -1:
            continue

        row = _products.iloc[idx]

        # Rating filter
        if min_rating > 0:
            rating = float(row.get("rating", 0))
            if rating < min_rating:
                continue

        # Price filter
        if max_price is not None:
            price = float(row.get("discounted_price", 0))
            if price > max_price:
                continue

        # Category filter
        if category_filter:
            category_text = str(row.get("category", "")).lower()

            if category_filter.lower() not in category_text:
                continue

        results.append(
            {
                "product_id": str(row.get("product_id", "")),
                "product_name": str(row.get("product_name", "")),
                "category": str(row.get("category", "")),
                "discounted_price": float(
                    row.get("discounted_price", 0)
                ),
                "actual_price": float(
                    row.get("actual_price", 0)
                ),
                "rating": float(row.get("rating", 0)),
                "rating_count": int(
                    row.get("rating_count", 0)
                ),
                "about_product": str(
                    row.get("about_product", "")
                )[:300],
                "similarity_score": round(float(score), 4),
            }
        )

        if len(results) >= top_k:
            break

    return results


if __name__ == "__main__":

    load_search_engine()

    test_queries = [
        "wireless earbuds",
        "iphone charger",
        "bluetooth speaker",
        "gaming keyboard",
        "laptop accessories",
    ]

    for query in test_queries:

        print("\n" + "=" * 60)
        print(f"🔍 Query: {query}")
        print("=" * 60)

        results = search_products(query, top_k=3)

        for i, product in enumerate(results, start=1):

            print(
                f"{i}. {product['product_name'][:80]}"
            )
            print(
                f"   ⭐ {product['rating']} | ₹{product['discounted_price']} | Score: {product['similarity_score']}"
            )