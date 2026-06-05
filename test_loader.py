from app.recommendation.data_loader import load_products

df = load_products()

print(df.head())

print("\nCombined Text Sample:\n")

print(df["combined_text"].iloc[0])