export default function ProductCard({ product }) {
  return (
    <div className="bg-gray-800 border border-gray-700 rounded-xl p-4 text-sm hover:border-blue-500 transition-all">
      <p className="text-white font-medium leading-snug line-clamp-2 mb-2">
        {product.product_name}
      </p>
      <div className="flex items-center justify-between mt-auto">
        <span className="text-green-400 font-semibold">
          ₹{product.discounted_price?.toLocaleString("en-IN")}
        </span>
        <span className="text-yellow-400 text-xs">
          ⭐ {product.rating}
        </span>
      </div>
      {product.actual_price && product.actual_price > product.discounted_price && (
        <p className="text-gray-500 text-xs mt-1 line-through">
          ₹{product.actual_price?.toLocaleString("en-IN")}
        </p>
      )}
    </div>
  )
}