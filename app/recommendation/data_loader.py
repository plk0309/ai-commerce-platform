import pandas as pd
import numpy as np
import re

from pathlib import Path

DATASET_PATH = Path("datasets/products.csv")


def clean_price(val: str) -> float:
    """Remove ₹ and commas → float. e.g. '₹1,099' → 1099.0"""
    try:
        return float(re.sub(r'[₹,\s]', '', str(val)))
    except:
        return 0.0


def clean_discount(val: str) -> float:
    """'64%' → 64.0"""
    try:
        return float(str(val).replace('%', '').strip())
    except:
        return 0.0


def clean_rating_count(val: str) -> int:
    """'24,269' → 24269"""
    try:
        return int(str(val).replace(',', '').strip())
    except:
        return 0


def get_main_category(category: str) -> str:
    """'Computers&Accessories|Cables|...' → 'Computers&Accessories'"""
    if pd.isna(category):
        return ""
    return str(category).split('|')[0].strip()


def get_sub_category(category: str) -> str:
    """Returns the last part of the category pipe chain"""
    if pd.isna(category):
        return ""
    parts = str(category).split('|')
    return parts[-1].strip() if len(parts) > 1 else ""


def load_products() -> pd.DataFrame:
    """
    Load and preprocess products.csv.
    Cleans prices, rating, discount.
    Creates 'combined_text' for embedding.
    Creates 'main_category' and 'sub_category' from pipe-separated category.
    """
    df = pd.read_csv(DATASET_PATH)
    print(f"📦 Loaded {len(df)} products | Columns: {list(df.columns)}")

    # ── Clean numeric fields ────────────────────────────────
    df['discounted_price'] = df['discounted_price'].apply(clean_price)
    df['actual_price']     = df['actual_price'].apply(clean_price)
    df['discount_percentage'] = df['discount_percentage'].apply(clean_discount)
    df['rating_count']     = df['rating_count'].apply(clean_rating_count)
    df['rating']           = pd.to_numeric(df['rating'], errors='coerce').fillna(0.0)

    # ── Category splitting ──────────────────────────────────
    df['main_category'] = df['category'].apply(get_main_category)
    df['sub_category']  = df['category'].apply(get_sub_category)

    # ── Fill NaN in text columns ────────────────────────────
    text_cols = ['product_name', 'about_product',
                 'review_title', 'review_content',
                 'main_category', 'sub_category']
    for col in text_cols:
        df[col] = df[col].fillna("")

    # ── Build combined_text for embeddings ──────────────────
    # Order matters: product_name first (most important signal)
    # about_product is the richest semantic field
    # review_title adds real user language ("great for gym", "fast charging")
    df['combined_text'] = (
        df['product_name']    + " " +
        df['main_category']  + " " +
        df['sub_category']   + " " +
        df['about_product']  + " " +
        df['review_title']
    )

    # ── Add integer index as product_idx ────────────────────
    df['product_idx'] = df.index

    df = df.reset_index(drop=True)
    print(f"✅ Preprocessing done. Shape: {df.shape}")
    print(f"   Sample combined_text[0]:\n   {df['combined_text'].iloc[0][:200]}")
    return df


if __name__ == "__main__":
    df = load_products()
    print("\nSample row:")
    print(df[['product_name', 'discounted_price',
              'rating', 'main_category']].head(3))