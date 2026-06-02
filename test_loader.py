from app.recommendation.data_loader import load_products

df = load_products()

print(df.head())
print("\n")
print(df["combined_text"][0])