import { useState, useRef, useEffect } from "react"
import axios from "axios"
import MessageBubble from "./MessageBubble"
import ProductCard from "./ProductCard"

const API = "http://127.0.0.1:8000/api/v1/chat"

const WELCOME = {
  customer: "Hi! I'm your Shopping Assistant. Tell me what you're looking for or your budget and I'll find the best products for you!",
  admin: "Hi! I'm your Analytics Assistant. Ask me about revenue, top products, sales trends, anomalies, or customer stats.",
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

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  // Reset chat when role changes
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

  const isAdmin = role === "admin"
  const accent = isAdmin ? "violet" : "indigo"

  return (
    <div className="w-full max-w-3xl flex flex-col bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm" style={{ height: "75vh" }}>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-5 space-y-4">
        {messages.map((msg, i) => (
          <div key={i}>
            <MessageBubble message={msg} accent={accent} />
            {msg.products?.length > 0 && (
              <div className="mt-3 ml-10 grid grid-cols-2 gap-3">
                {msg.products.map((p, j) => <ProductCard key={j} product={p} />)}
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex gap-2 items-center ml-10">
            {[0, 150, 300].map(delay => (
              <div key={delay} className="w-2 h-2 bg-slate-300 rounded-full animate-bounce"
                style={{ animationDelay: `${delay}ms` }} />
            ))}
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-slate-100 flex gap-3">
        <input
          className="flex-1 bg-slate-50 border border-slate-200 text-slate-800 placeholder-slate-400 rounded-xl px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-indigo-200 focus:border-indigo-400 transition-all"
          placeholder={PLACEHOLDER[role]}
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === "Enter" && !e.shiftKey && (e.preventDefault(), sendMessage())}
        />
        <button
          onClick={sendMessage}
          disabled={loading}
          className={`px-5 py-3 rounded-xl text-sm font-medium text-white disabled:opacity-50 transition-all ${isAdmin ? "bg-violet-600 hover:bg-violet-700" : "bg-indigo-600 hover:bg-indigo-700"}`}
        >
          Send
        </button>
      </div>
    </div>
  )
}