import { useState, useRef, useEffect } from "react"
import axios from "axios"
import MessageBubble from "./MessageBubble"
import ProductCard from "./ProductCard"

const API = "http://127.0.0.1:8000/api/v1/chat"

const WELCOME = {
  customer: "Hi! Tell me what you're looking for or your budget and I'll find the best products for you!",
  admin: "Hi! Ask me about revenue, top products, sales trends, anomalies, or customer stats.",
}

const PLACEHOLDER = {
  customer: "Ask me anything — budget, category, brand...",
  admin: "Ask about revenue, top products, trends...",
}

export default function ChatWindow({ role }) {
  const sessionId = useRef("session_" + Math.random().toString(36).slice(2, 9))
  const [messages, setMessages] = useState([
    { from: "bot", text: WELCOME[role], products: [] }
  ])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)
  const isAdmin = role === "admin"

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  useEffect(() => {
    setMessages([{ from: "bot", text: WELCOME[role], products: [] }])
    setInput("")
    sessionId.current = "session_" + Math.random().toString(36).slice(2, 9)
  }, [role])

  const sendMessage = async () => {
    const text = input.trim()
    if (!text || loading) return
    setMessages(prev => [...prev, { from: "user", text }])
    setInput("")
    setLoading(true)
    try {
      const res = await axios.post(API, {
        message: text,
        session_id: sessionId.current,
        role,
      })
      setMessages(prev => [...prev, {
        from: "bot",
        text: res.data.reply,
        products: res.data.products || [],
        type: res.data.type,
      }])
    } catch {
      setMessages(prev => [...prev, {
        from: "bot",
        text: "Something went wrong. Please check if the backend is running.",
        products: [],
      }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      width: "100%", maxWidth: 760,
      display: "flex", flexDirection: "column",
      background: "#0a0f0a",
      border: "1px solid #1f331f",
      borderRadius: 16, overflow: "hidden",
      height: "75vh",
    }}>

      {/* Online bar */}
      <div style={{
        padding: "10px 18px",
        borderBottom: "1px solid #1f331f",
        display: "flex", alignItems: "center", justifyContent: "space-between",
        background: "#0c160c"
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <div style={{ width: 7, height: 7, borderRadius: "50%", background: "#22c55e" }} />
          <span style={{ fontSize: 11, color: "#6b8f6b" }}>
            {isAdmin ? "LLaMA 3.1 · Analytics Engine" : "LLaMA 3.1 · FAISS Search"}
          </span>
        </div>
        <span style={{ fontSize: 11, color: "#22c55e" }}>● Online</span>
      </div>

      {/* Messages */}
      <div style={{ flex: 1, overflowY: "auto", padding: "18px", display: "flex", flexDirection: "column", gap: 14 }}>
        {messages.map((msg, i) => (
          <div key={i}>
            <MessageBubble message={msg} isAdmin={isAdmin} />
            {msg.products?.length > 0 && (
              <div style={{
                marginTop: 10, marginLeft: 34,
                display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8
              }}>
                {msg.products.map((p, j) => <ProductCard key={j} product={p} />)}
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div style={{ display: "flex", gap: 8, alignItems: "center", marginLeft: 34 }}>
            {[0, 150, 300].map(d => (
              <div key={d} style={{
                width: 6, height: 6, borderRadius: "50%", background: "#6b8f6b",
                animation: "bounce 1s infinite",
                animationDelay: `${d}ms`
              }} />
            ))}
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div style={{
        padding: "12px 16px", borderTop: "1px solid #1f331f",
        display: "flex", gap: 10, alignItems: "center",
        background: "#0c160c"
      }}>
        <input
          style={{
            flex: 1, background: "#0f1a0f",
            border: "1px solid #1f331f", borderRadius: 10,
            padding: "10px 14px", fontSize: 13,
            color: "#c8e8c8", outline: "none",
            fontFamily: "inherit"
          }}
          placeholder={PLACEHOLDER[role]}
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === "Enter" && !e.shiftKey && (e.preventDefault(), sendMessage())}
          onFocus={e => e.target.style.borderColor = isAdmin ? "#f0b42966" : "#22c55e66"}
          onBlur={e => e.target.style.borderColor = "#1f331f"}
        />
        <button
          onClick={sendMessage}
          disabled={loading}
          style={{
            width: 38, height: 38, borderRadius: 10, border: "none",
            background: isAdmin ? "#f0b429" : "#22c55e",
            display: "flex", alignItems: "center", justifyContent: "center",
            cursor: "pointer", opacity: loading ? 0.5 : 1, flexShrink: 0
          }}
        >
          <svg width="16" height="16" fill="none" stroke={isAdmin ? "#0a0f0a" : "#0a0f0a"} strokeWidth="2.5" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z" />
          </svg>
        </button>
      </div>

      <style>{`
        @keyframes bounce {
          0%, 80%, 100% { transform: translateY(0); }
          40% { transform: translateY(-5px); }
        }
      `}</style>
    </div>
  )
}