import ChatWindow from "../components/ChatWindow"

export default function ChatPage({ role, onLogout }) {
  const isAdmin = role === "admin"

  return (
    <div style={{
      minHeight: "100vh", background: "#0a0f0a",
      display: "flex", flexDirection: "column",
      alignItems: "center", paddingTop: 32, paddingBottom: 32, paddingLeft: 16, paddingRight: 16
    }}>

      {/* Topbar */}
      <div style={{
        width: "100%", maxWidth: 760,
        display: "flex", alignItems: "center", justifyContent: "space-between",
        marginBottom: 20
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <div style={{
            width: 38, height: 38, borderRadius: 10,
            background: isAdmin ? "#f0b42918" : "#22c55e18",
            border: `1px solid ${isAdmin ? "#f0b42933" : "#22c55e33"}`,
            display: "flex", alignItems: "center", justifyContent: "center"
          }}>
            <svg width="17" height="17" fill="none" stroke={isAdmin ? "#f0b429" : "#22c55e"} strokeWidth="2" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round"
                d={isAdmin
                  ? "M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                  : "M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"}
              />
            </svg>
          </div>
          <div>
            <p style={{ fontSize: 14, fontWeight: 500, color: "#e8f5e8" }}>
              {isAdmin ? "Analytics Assistant" : "Shopping Assistant"}
            </p>
            <p style={{ fontSize: 11, color: "#6b8f6b" }}>
              {isAdmin ? "Business insights & revenue analytics" : "AI-powered product recommendations"}
            </p>
          </div>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <span style={{
            fontSize: 11, fontWeight: 500,
            padding: "3px 10px", borderRadius: 20,
            background: isAdmin ? "#f0b42918" : "#22c55e18",
            border: `1px solid ${isAdmin ? "#f0b42933" : "#22c55e33"}`,
            color: isAdmin ? "#f0b429" : "#22c55e"
          }}>
            {isAdmin ? "Admin" : "Customer"}
          </span>
          <button onClick={onLogout} style={{
            fontSize: 11, color: "#6b8f6b",
            border: "1px solid #1f331f", padding: "3px 10px",
            borderRadius: 20, background: "transparent", cursor: "pointer"
          }}>
            Switch role
          </button>
        </div>
      </div>

      <ChatWindow role={role} />
    </div>
  )
}