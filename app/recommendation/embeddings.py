import numpy as np
import os
import pickle
from sentence_transformers import SentenceTransformer
from app.recommendation.data_loader import load_products

# ─── Config ───────────────────────────────────────────────
MODEL_NAME       = "all-MiniLM-L6-v2"   # fast, lightweight, great quality
ARTIFACTS_DIR    = "artifacts"
EMBEDDINGS_PATH  = "artifacts/product_embeddings.npy"
PRODUCTS_PKL     = "artifacts/products_df.pkl"
# ──────────────────────────────────────────────────────────

def generate_embeddings(force_regenerate: bool = False) -> tuple:
    """
    Generate and save product embeddings.
    Returns: (embeddings np.array, products DataFrame)
    
    force_regenerate=True  → always regenerate even if file exists
    force_regenerate=False → load from disk if already generated (saves time)
    """
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    
    # If embeddings already exist, load them (skip regenerating)
    if not force_regenerate and os.path.exists(EMBEDDINGS_PATH):
        print("⚡ Loading existing embeddings from disk...")
        embeddings = np.load(EMBEDDINGS_PATH)
        with open(PRODUCTS_PKL, 'rb') as f:
            df = pickle.load(f)
        print(f"✅ Loaded {len(embeddings)} embeddings. Shape: {embeddings.shape}")
        return embeddings, df
    
    # Load and preprocess products
    print("📦 Loading products dataset...")
    df = load_products()
    
    # Load SentenceTransformer model
    print(f"🤖 Loading model: {MODEL_NAME}...")
    model = SentenceTransformer(MODEL_NAME)
    
    # Generate embeddings from combined_text
    texts = df['combined_text'].tolist()
    print(f"⚙️  Generating embeddings for {len(texts)} products...")
    print("   (This takes ~30-60 seconds the first time)")
    
    embeddings = model.encode(
        texts,
        batch_size=64,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True   # L2 normalize for cosine similarity
    )
    
    # Save to disk
    np.save(EMBEDDINGS_PATH, embeddings)
    with open(PRODUCTS_PKL, 'wb') as f:
        pickle.dump(df, f)
    
    print(f"✅ Embeddings saved to {EMBEDDINGS_PATH}")
    print(f"   Shape: {embeddings.shape}  (products × dimensions)")
    
    return embeddings, df


if __name__ == "__main__":
    embeddings, df = generate_embeddings(force_regenerate=True)
    print(f"\nSample embedding vector (first 5 dims): {embeddings[0][:5]}")