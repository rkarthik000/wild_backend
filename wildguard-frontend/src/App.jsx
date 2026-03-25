import { useState } from "react";
import LoginPage from "./LoginPage";
import WildGuardDashboard from "./WildGuardDashboard";

export default function App() {
  const [user, setUser] = useState(null);

  if (!user) return <LoginPage onLogin={setUser} />;
  return <WildGuardDashboard user={user} onLogout={() => setUser(null)} />;
}
