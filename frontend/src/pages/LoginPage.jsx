export default function LoginPage({ onSelect }) {
  return (
    <div style={{
      minHeight: "100vh", background: "#0a0f0a",
      display: "flex", flexDirection: "column",
      alignItems: "center", justifyContent: "center", padding: "32px 16px"
    }}>

      {/* Logo */}
      <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 6 }}>
        <div style={{
          width: 42, height: 42, background: "#22c55e",
          borderRadius: 12, display: "flex", alignItems: "center", justifyContent: "center"
        }}>
          <svg width="20" height="20" fill="none" stroke="#0a0f0a" strokeWidth="2.5" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        </div>
        <span style={{ fontSize: 22, fontWeight: 500, color: "#e8f5e8" }}>ShopAI</span>
      </div>
      <p style={{ fontSize: 12, color: "#6b8f6b", marginBottom: 32 }}>AI-powered Commerce Platform</p>

      <p style={{ fontSize: 12, color: "#6b8f6b", marginBottom: 16 }}>Select how you want to continue</p>

      {/* Cards */}
      <div style={{ display: "flex", gap: 14, width: "100%", maxWidth: 480 }}>

        {/* Customer */}
        <button onClick={() => onSelect("customer")} style={{
          flex: 1, background: "#0f1a0f", border: "1px solid #1f331f",
          borderRadius: 14, padding: "20px 16px", textAlign: "left",
          cursor: "pointer", transition: "all 0.2s"
        }}
          onMouseEnter={e => { e.currentTarget.style.borderColor = "#22c55e"; e.currentTarget.style.background = "#142014"; }}
          onMouseLeave={e => { e.currentTarget.style.borderColor = "#1f331f"; e.currentTarget.style.background = "#0f1a0f"; }}
        >
          <div style={{
            width: 40, height: 40, background: "#22c55e18",
            border: "1px solid #22c55e33", borderRadius: 10,
            display: "flex", alignItems: "center", justifyContent: "center", marginBottom: 14
          }}>
            <svg width="18" height="18" fill="none" stroke="#22c55e" strokeWidth="2" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
            </svg>
          </div>
          <p style={{ fontSize: 14, fontWeight: 500, color: "#e8f5e8", marginBottom: 6 }}>Customer</p>
          <p style={{ fontSize: 12, color: "#6b8f6b", lineHeight: 1.6, marginBottom: 14 }}>
            Browse products, get AI-powered recommendations and find the best deals.
          </p>
          <div style={{ display: "flex", alignItems: "center", gap: 4, fontSize: 12, fontWeight: 500, color: "#22c55e" }}>
            Shop now
            <svg width="14" height="14" fill="none" stroke="#22c55e" strokeWidth="2" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
            </svg>
          </div>
        </button>

        {/* Admin */}
        <button onClick={() => onSelect("admin")} style={{
          flex: 1, background: "#0f1a0f", border: "1px solid #1f331f",
          borderRadius: 14, padding: "20px 16px", textAlign: "left",
          cursor: "pointer", transition: "all 0.2s"
        }}
          onMouseEnter={e => { e.currentTarget.style.borderColor = "#f0b429"; e.currentTarget.style.background = "#1a160a"; }}
          onMouseLeave={e => { e.currentTarget.style.borderColor = "#1f331f"; e.currentTarget.style.background = "#0f1a0f"; }}
        >
          <div style={{
            width: 40, height: 40, background: "#f0b42918",
            border: "1px solid #f0b42933", borderRadius: 10,
            display: "flex", alignItems: "center", justifyContent: "center", marginBottom: 14
          }}>
            <svg width="18" height="18" fill="none" stroke="#f0b429" strokeWidth="2" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <p style={{ fontSize: 14, fontWeight: 500, color: "#e8f5e8", marginBottom: 6 }}>Admin</p>
          <p style={{ fontSize: 12, color: "#6b8f6b", lineHeight: 1.6, marginBottom: 14 }}>
            View sales analytics, revenue trends, top products and business insights.
          </p>
          <div style={{ display: "flex", alignItems: "center", gap: 4, fontSize: 12, fontWeight: 500, color: "#f0b429" }}>
            View dashboard
            <svg width="14" height="14" fill="none" stroke="#f0b429" strokeWidth="2" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
            </svg>
          </div>
        </button>
      </div>

      <p style={{ fontSize: 11, color: "#2a3f2a", marginTop: 28 }}>AI Commerce Platform · Katharos Techie</p>
    </div>
  )
}