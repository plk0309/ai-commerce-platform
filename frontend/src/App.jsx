import { useState } from "react"
import LoginPage from "./pages/LoginPage"
import ChatPage from "./pages/ChatPage"

export default function App() {
  const [role, setRole] = useState(null) // null = not logged in

  if (!role) return <LoginPage onSelect={setRole} />
  return <ChatPage role={role} onLogout={() => setRole(null)} />
}