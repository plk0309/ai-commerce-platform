export default function MessageBubble({ message, isAdmin }) {
  const isUser = message.from === "user"
  const isClarify = message.type === "shopping_clarify"

  return (
    <div style={{ display: "flex", justifyContent: isUser ? "flex-end" : "flex-start", gap: 8 }}>

      {/* Bot avatar */}
      {!isUser && (
        <div style={{
          width: 28, height: 28, borderRadius: "50%", flexShrink: 0,
          background: isAdmin ? "#f0b42918" : "#22c55e18",
          border: `1px solid ${isAdmin ? "#f0b42933" : "#22c55e33"}`,
          display: "flex", alignItems: "center", justifyContent: "center"
        }}>
          <svg width="13" height="13" fill="none" stroke={isAdmin ? "#f0b429" : "#22c55e"} strokeWidth="2" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" d="M9 3H5a2 2 0 00-2 2v4m6-6h10a2 2 0 012 2v4M9 3v18m0 0h10a2 2 0 002-2V9M9 21H5a2 2 0 01-2-2V9m0 0h18" />
          </svg>
        </div>
      )}

      <div>
        {/* Clarify badge */}
        {isClarify && (
          <div style={{
            display: "inline-flex", alignItems: "center", gap: 4,
            background: "#f0b42912", border: "1px solid #f0b42933",
            borderRadius: 20, padding: "2px 8px",
            fontSize: 10, color: "#f0b429", marginBottom: 5
          }}>
            <svg width="10" height="10" fill="none" stroke="#f0b429" strokeWidth="2" viewBox="0 0 24 24">
              <circle cx="12" cy="12" r="10" /><path strokeLinecap="round" d="M12 8v4m0 4h.01" />
            </svg>
            Clarifying
          </div>
        )}

        {/* Bubble */}
        <div style={{
          maxWidth: "75%",
          padding: "9px 13px",
          borderRadius: isUser ? "12px 3px 12px 12px" : "3px 12px 12px 12px",
          fontSize: 13, lineHeight: 1.6,
          background: isUser
            ? (isAdmin ? "#f0b429" : "#22c55e")
            : "#0f1a0f",
          color: isUser ? "#0a0f0a" : "#c8e8c8",
          border: isUser ? "none" : "1px solid #1f331f",
          fontWeight: isUser ? 500 : 400,
        }}>
          {message.text}
        </div>
      </div>

      {/* User avatar */}
      {isUser && (
        <div style={{
          width: 28, height: 28, borderRadius: "50%", flexShrink: 0,
          background: isAdmin ? "#f0b429" : "#22c55e",
          display: "flex", alignItems: "center", justifyContent: "center",
          fontSize: 11, fontWeight: 500, color: "#0a0f0a"
        }}>
          P
        </div>
      )}
    </div>
  )
}