import ChatWindow from "../components/ChatWindow"

export default function ChatPage({ role, onLogout }) {
  const isAdmin = role === "admin"

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col items-center py-8 px-4">

      {/* Topbar */}
      <div className="w-full max-w-3xl flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className={`w-9 h-9 rounded-xl flex items-center justify-center ${isAdmin ? "bg-violet-600" : "bg-indigo-600"}`}>
            <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d={isAdmin
                  ? "M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                  : "M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"}
              />
            </svg>
          </div>
          <div>
            <h1 className="text-base font-semibold text-slate-900">
              {isAdmin ? "Analytics Assistant" : "Shopping Assistant"}
            </h1>
            <p className="text-xs text-slate-400">
              {isAdmin ? "Business insights & revenue analytics" : "AI-powered product recommendations"}
            </p>
          </div>
        </div>

        {/* Role badge + logout */}
        <div className="flex items-center gap-3">
          <span className={`text-xs font-medium px-3 py-1 rounded-full ${isAdmin ? "bg-violet-50 text-violet-600" : "bg-indigo-50 text-indigo-600"}`}>
            {isAdmin ? "Admin" : "Customer"}
          </span>
          <button
            onClick={onLogout}
            className="text-xs text-slate-400 hover:text-slate-600 border border-slate-200 px-3 py-1 rounded-full hover:border-slate-300 transition-all"
          >
            Switch role
          </button>
        </div>
      </div>

      {/* Chat */}
      <ChatWindow role={role} />
    </div>
  )
}