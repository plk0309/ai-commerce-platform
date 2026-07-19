export default function ProductCard({ product }) {
  const hasDiscount = product.actual_price && product.actual_price > product.discounted_price

  return (
    <div style={{
      background: "#0f1a0f", border: "1px solid #1f331f",
      borderRadius: 10, padding: "10px 12px",
      transition: "border-color 0.2s", cursor: "pointer"
    }}
      onMouseEnter={e => e.currentTarget.style.borderColor = "#22c55e44"}
      onMouseLeave={e => e.currentTarget.style.borderColor = "#1f331f"}
    >
      <p style={{
        fontSize: 12, color: "#c8e8c8", lineHeight: 1.4,
        marginBottom: 8,
        display: "-webkit-box", WebkitLineClamp: 2,
        WebkitBoxOrient: "vertical", overflow: "hidden"
      }}>
        {product.product_name}
      </p>

      <p style={{ fontSize: 14, fontWeight: 500, color: "#22c55e" }}>
        ₹{product.discounted_price?.toLocaleString("en-IN")}
      </p>

      {hasDiscount && (
        <p style={{ fontSize: 11, color: "#2a4a2a", textDecoration: "line-through", marginTop: 1 }}>
          ₹{product.actual_price?.toLocaleString("en-IN")}
        </p>
      )}

      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginTop: 6 }}>
        <span style={{ fontSize: 11, color: "#6b8f6b" }}>
          <span style={{ color: "#f0b429" }}>★</span> {product.rating}
        </span>
        {hasDiscount && (
          <span style={{
            fontSize: 10, fontWeight: 500,
            background: "#22c55e18", color: "#22c55e",
            padding: "2px 6px", borderRadius: 4
          }}>
            {Math.round((1 - product.discounted_price / product.actual_price) * 100)}% off
          </span>
        )}
      </div>
    </div>
  )
}