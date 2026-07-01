export default function LoginPage({ onSelect }) {
  return (
    <div className="min-h-screen bg-slate-50 flex flex-col items-center justify-center px-4">

      {/* Logo */}
      <div className="mb-10 text-center">
        <div className="w-12 h-12 bg-indigo-600 rounded-xl flex items-center justify-center mx-auto mb-4">
          <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
              d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        </div>
        <h1 className="text-2xl font-semibold text-slate-900">ShopAI</h1>
        <p className="text-slate-400 text-sm mt-1">AI-powered Commerce Platform</p>
      </div>

      {/* Heading */}
      <p className="text-slate-500 text-sm mb-6">Select how you want to continue</p>

      {/* Role Cards */}
      <div className="flex flex-col sm:flex-row gap-4 w-full max-w-lg">

        {/* Customer Card */}
        <button
          onClick={() => onSelect("customer")}
          className="flex-1 bg-white border border-slate-200 rounded-2xl p-6 text-left hover:border-indigo-400 hover:shadow-md transition-all group"
        >
          <div className="w-11 h-11 bg-indigo-50 rounded-xl flex items-center justify-center mb-4 group-hover:bg-indigo-100 transition-colors">
            <svg className="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
            </svg>
          </div>
          <h2 className="text-base font-semibold text-slate-900 mb-1">Customer</h2>
          <p className="text-slate-400 text-sm leading-relaxed">
            Browse products, get AI-powered recommendations, and find the best deals.
          </p>
          <div className="mt-4 flex items-center gap-1 text-indigo-600 text-sm font-medium">
            Shop now
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </div>
        </button>

        {/* Admin Card */}
        <button
          onClick={() => onSelect("admin")}
          className="flex-1 bg-white border border-slate-200 rounded-2xl p-6 text-left hover:border-violet-400 hover:shadow-md transition-all group"
        >
          <div className="w-11 h-11 bg-violet-50 rounded-xl flex items-center justify-center mb-4 group-hover:bg-violet-100 transition-colors">
            <svg className="w-5 h-5 text-violet-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <h2 className="text-base font-semibold text-slate-900 mb-1">Admin</h2>
          <p className="text-slate-400 text-sm leading-relaxed">
            View sales analytics, revenue trends, top products, and business insights.
          </p>
          <div className="mt-4 flex items-center gap-1 text-violet-600 text-sm font-medium">
            View dashboard
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </div>
        </button>
      </div>

      <p className="text-slate-300 text-xs mt-8">AI Commerce Platform · Katharos Techie</p>
    </div>
  )
}