import { useState } from "react";

export default function LoginPage({ onLogin }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const DEMO_USERS = [
    { email: "ranger@wildguard.io", password: "ranger123", role: "Field Ranger", badge: "R-001" },
    { email: "admin@wildguard.io", password: "admin123", role: "Administrator", badge: "A-001" },
    { email: "analyst@wildguard.io", password: "analyst123", role: "Data Analyst", badge: "D-001" },
  ];

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    await new Promise(r => setTimeout(r, 900));
    const user = DEMO_USERS.find(u => u.email === email && u.password === password);
    if (user) {
      onLogin(user);
    } else {
      setError("Invalid credentials. Try ranger@wildguard.io / ranger123");
    }
    setLoading(false);
  };

  return (
    <div style={{
      minHeight: "100vh",
      background: "#050a08",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      fontFamily: "'Space Mono', monospace",
      position: "relative",
      overflow: "hidden",
    }}>
      {/* Animated background grid */}
      <div style={{
        position: "absolute", inset: 0,
        backgroundImage: `
          linear-gradient(rgba(0,255,100,0.03) 1px, transparent 1px),
          linear-gradient(90deg, rgba(0,255,100,0.03) 1px, transparent 1px)
        `,
        backgroundSize: "40px 40px",
        animation: "gridMove 20s linear infinite",
      }} />

      {/* Glow orbs */}
      <div style={{
        position: "absolute", width: 400, height: 400,
        background: "radial-gradient(circle, rgba(0,255,100,0.06) 0%, transparent 70%)",
        top: "10%", left: "15%", borderRadius: "50%",
      }} />
      <div style={{
        position: "absolute", width: 300, height: 300,
        background: "radial-gradient(circle, rgba(0,180,255,0.05) 0%, transparent 70%)",
        bottom: "20%", right: "10%", borderRadius: "50%",
      }} />

      <div style={{
        width: 420,
        position: "relative",
        zIndex: 10,
      }}>
        {/* Header */}
        <div style={{ textAlign: "center", marginBottom: 40 }}>
          <div style={{
            display: "inline-flex", alignItems: "center", justifyContent: "center",
            width: 64, height: 64,
            border: "1px solid rgba(0,255,100,0.3)",
            borderRadius: 16,
            marginBottom: 20,
            background: "rgba(0,255,100,0.05)",
            fontSize: 28,
          }}>🌿</div>
          <h1 style={{
            fontSize: 26, fontWeight: 700, color: "#fff",
            letterSpacing: "0.15em", margin: 0,
            textTransform: "uppercase",
          }}>WildGuard</h1>
          <p style={{
            color: "rgba(0,255,100,0.6)", fontSize: 11,
            letterSpacing: "0.3em", margin: "8px 0 0",
            textTransform: "uppercase",
          }}>Endangered Species Protection System</p>
        </div>

        {/* Card */}
        <div style={{
          background: "rgba(255,255,255,0.03)",
          border: "1px solid rgba(255,255,255,0.08)",
          borderRadius: 20,
          padding: "36px 40px",
          backdropFilter: "blur(20px)",
        }}>
          <p style={{
            color: "rgba(255,255,255,0.4)", fontSize: 11,
            letterSpacing: "0.2em", textTransform: "uppercase",
            marginBottom: 24, marginTop: 0,
          }}>Authorized Personnel Only</p>

          <form onSubmit={handleLogin}>
            <div style={{ marginBottom: 16 }}>
              <label style={{
                display: "block", color: "rgba(255,255,255,0.5)",
                fontSize: 10, letterSpacing: "0.2em",
                textTransform: "uppercase", marginBottom: 8,
              }}>Email</label>
              <input
                type="email"
                value={email}
                onChange={e => setEmail(e.target.value)}
                placeholder="ranger@wildguard.io"
                required
                style={{
                  width: "100%", boxSizing: "border-box",
                  background: "rgba(255,255,255,0.04)",
                  border: "1px solid rgba(255,255,255,0.1)",
                  borderRadius: 10,
                  padding: "12px 16px",
                  color: "#fff", fontSize: 13,
                  fontFamily: "'Space Mono', monospace",
                  outline: "none",
                  transition: "border-color 0.2s",
                }}
                onFocus={e => e.target.style.borderColor = "rgba(0,255,100,0.4)"}
                onBlur={e => e.target.style.borderColor = "rgba(255,255,255,0.1)"}
              />
            </div>

            <div style={{ marginBottom: 24 }}>
              <label style={{
                display: "block", color: "rgba(255,255,255,0.5)",
                fontSize: 10, letterSpacing: "0.2em",
                textTransform: "uppercase", marginBottom: 8,
              }}>Password</label>
              <input
                type="password"
                value={password}
                onChange={e => setPassword(e.target.value)}
                placeholder="••••••••"
                required
                style={{
                  width: "100%", boxSizing: "border-box",
                  background: "rgba(255,255,255,0.04)",
                  border: "1px solid rgba(255,255,255,0.1)",
                  borderRadius: 10,
                  padding: "12px 16px",
                  color: "#fff", fontSize: 13,
                  fontFamily: "'Space Mono', monospace",
                  outline: "none",
                  transition: "border-color 0.2s",
                }}
                onFocus={e => e.target.style.borderColor = "rgba(0,255,100,0.4)"}
                onBlur={e => e.target.style.borderColor = "rgba(255,255,255,0.1)"}
              />
            </div>

            {error && (
              <div style={{
                background: "rgba(255,60,60,0.1)",
                border: "1px solid rgba(255,60,60,0.3)",
                borderRadius: 8, padding: "10px 14px",
                color: "#ff6060", fontSize: 12,
                marginBottom: 16,
              }}>{error}</div>
            )}

            <button
              type="submit"
              disabled={loading}
              style={{
                width: "100%",
                background: loading ? "rgba(0,255,100,0.1)" : "rgba(0,255,100,0.15)",
                border: "1px solid rgba(0,255,100,0.4)",
                borderRadius: 10,
                padding: "13px",
                color: "#00ff64",
                fontSize: 12,
                letterSpacing: "0.2em",
                textTransform: "uppercase",
                fontFamily: "'Space Mono', monospace",
                cursor: loading ? "not-allowed" : "pointer",
                transition: "all 0.2s",
              }}
            >
              {loading ? "Authenticating..." : "Access System"}
            </button>
          </form>

          {/* Demo credentials */}
          <div style={{
            marginTop: 28,
            paddingTop: 20,
            borderTop: "1px solid rgba(255,255,255,0.06)",
          }}>
            <p style={{
              color: "rgba(255,255,255,0.25)", fontSize: 10,
              letterSpacing: "0.15em", textTransform: "uppercase",
              marginBottom: 10, marginTop: 0,
            }}>Demo Credentials</p>
            {DEMO_USERS.map(u => (
              <div
                key={u.email}
                onClick={() => { setEmail(u.email); setPassword(u.password); }}
                style={{
                  padding: "8px 12px",
                  borderRadius: 8,
                  cursor: "pointer",
                  marginBottom: 4,
                  display: "flex", justifyContent: "space-between", alignItems: "center",
                  transition: "background 0.15s",
                  background: "rgba(255,255,255,0.02)",
                }}
                onMouseEnter={e => e.currentTarget.style.background = "rgba(0,255,100,0.05)"}
                onMouseLeave={e => e.currentTarget.style.background = "rgba(255,255,255,0.02)"}
              >
                <span style={{ color: "rgba(255,255,255,0.4)", fontSize: 11 }}>{u.email}</span>
                <span style={{
                  color: "rgba(0,255,100,0.5)", fontSize: 10,
                  letterSpacing: "0.1em", textTransform: "uppercase",
                }}>{u.role}</span>
              </div>
            ))}
          </div>
        </div>

        <p style={{
          textAlign: "center", color: "rgba(255,255,255,0.15)",
          fontSize: 10, letterSpacing: "0.15em",
          textTransform: "uppercase", marginTop: 24,
        }}>WildGuard v2.0 · Protected System</p>
      </div>

      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&display=swap');
        @keyframes gridMove {
          0% { backgroundPosition: 0 0; }
          100% { backgroundPosition: 40px 40px; }
        }
      `}</style>
    </div>
  );
}
