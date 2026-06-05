import faiss
import numpy as np
import os
import pickle
from sentence_transformers import SentenceTransformer
from app.recommendation.embeddings import generate_embeddings

# ─── Config ───────────────────────────────────────────────
MODEL_NAME    = "all-MiniLM-L6-v2"
FAISS_PATH    = "artifacts/faiss_index.bin"
ARTIFACTS_DIR = "artifacts"
# ──────────────────────────────────────────────────────────

# Global objects (loaded once at startup)
_model    = None
_index    = None
_products = None


def build_faiss_index(embeddings: np.ndarray) -> faiss.IndexFlatIP:
    """
    Build a FAISS IndexFlatIP (Inner Product) index.
    Since embeddings are L2-normalized, inner product = cosine similarity.
    """
    dim = embeddings.shape[1]            # 384 for all-MiniLM-L6-v2
    index = faiss.IndexFlatIP(dim)        # cosine similarity
    index.add(embeddings.astype('float32'))
    faiss.write_index(index, FAISS_PATH)
    print(f"✅ FAISS index built with {index.ntotal} vectors → {FAISS_PATH}")
    return index


def load_search_engine():
    """
    Load model, FAISS index, and product DataFrame.
    Called once when the application starts.
    """
    global _model, _index, _products
    
    if _model is not None:
        return  # Already loaded
    
    print("🚀 Initializing Search Engine...")
    
    # Load embeddings and products
    embeddings, _products = generate_embeddings()
    
    # Build or load FAISS index
    if os.path.exists(FAISS_PATH):
        print("⚡ Loading existing FAISS index...")
        _index = faiss.read_index(FAISS_PATH)
    else:
        print("🔨 Building FAISS index...")
        _index = build_faiss_index(embeddings)
    
    # Load SentenceTransformer for query encoding
    print("🤖 Loading embedding model...")
    _model = SentenceTransformer(MODEL_NAME)
    
    print("✅ Search Engine ready!")


def search_products(query: str, top_k: int = 5, 
                    min_rating: float = 0.0,
                    max_price: float = None) -> list:
    """
    Semantic search for products.
    
    Args:
        query     : natural language query
        top_k     : number of results to return
        min_rating: filter products below this rating
        max_price : filter products above this price
    
    Returns: list of product dicts
    """
    load_search_engine()   # ensures everything is loaded
    
    # Encode query (normalize for cosine similarity)
    query_vec = _model.encode(
        [query],
        normalize_embeddings=True,
        convert_to_numpy=True
    ).astype('float32')
    
    # Search FAISS — fetch more results to allow for filtering
    fetch_k = min(top_k * 3, len(_products))
    scores, indices = _index.search(query_vec, fetch_k)
    
    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx == -1:
            continue
        
        row = _products.iloc[idx]
        
        # Apply filters
        if min_rating > 0 and row.get('rating', 0) < min_rating:
            continue
        if max_price and row.get('discounted_price', 0) > max_price:
            continue
        
        results.append({
            "product_id"        : int(idx),
            "product_name"      : row.get('product_name', ''),
            "category"          : row.get('category', ''),
            "discounted_price"  : row.get('discounted_price', 0),
            "actual_price"      : row.get('actual_price', 0),
            "rating"            : row.get('rating', 0),
            "about_product"     : row.get('about_product', '')[:300],
            "similarity_score"  : round(float(score), 4),
        })
        
        if len(results) >= top_k:
            break
    
    return results


if __name__ == "__main__":
    # Test queries
    test_queries = [
        "wireless earbuds for gym",
        "laptop for machine learning",
        "fast charging cable",
        "bluetooth speaker waterproof",
        "gaming keyboard mechanical",
    ]
    
    for q in test_queries:
        print(f"\n🔍 Query: '{q}'")
        results = search_products(q, top_k=3)
        for i, r in enumerate(results, 1):
            print(f"  {i}. {r['product_name'][:60]}")
            print(f"     Score: {r['similarity_score']} | ₹{r['discounted_price']} | ⭐ {r['rating']}")