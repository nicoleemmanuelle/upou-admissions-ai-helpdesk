import { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import { sendQuery } from "./api";

const UPOU_GREEN = "#8a1538";
const UPOU_DARK = "#6b102b";
const UPOU_MAROON = "#8a1538";
const UPOU_LIGHT_BG = "#FDF5F7";

function App() {
  const [messages, setMessages] = useState([
    {
      role: "bot",
      text: "Hello! I'm the **UPOU Admissions AI Helpdesk**. I can help you with questions about admissions, programs, requirements, and more. What would you like to know?",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    const trimmed = input.trim();
    if (!trimmed || loading) return;

    const userMsg = { role: "user", text: trimmed };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      console.log("Sending query:", JSON.stringify(trimmed));
      const response = await sendQuery(trimmed);
      console.log("Got response:", response?.substring(0, 100));
      setMessages((prev) => [...prev, { role: "bot", text: response }]);
    } catch (err) {
      console.error("API error:", err);
      setMessages((prev) => [
        ...prev,
        { role: "bot", text: `Sorry, something went wrong: ${err.message}` },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const quickQuestions = [
    "What are the admission requirements?",
    "What programs does UPOU offer?",
    "How do I apply for graduate studies?",
    "What are the tuition fees?",
  ];

  return (
    <div style={styles.page}>
      {/* Header */}
      <header style={styles.header}>
        <div style={styles.headerInner}>
          <div style={styles.logoArea}>
            <div style={styles.logoCircle}>
              <span style={styles.logoText}>UP</span>
            </div>
            <div>
              <h1 style={styles.title}>UPOU Admissions AI Helpdesk</h1>
              <p style={styles.subtitle}>University of the Philippines Open University</p>
            </div>
          </div>
          <div style={styles.statusBadge}>
            <span style={styles.statusDot}></span> Online
          </div>
        </div>
      </header>

      {/* Chat Area */}
      <main style={styles.chatContainer}>
        <div style={styles.messagesArea}>
          {messages.map((msg, i) => (
            <div
              key={i}
              style={{
                ...styles.messageBubbleWrap,
                justifyContent: msg.role === "user" ? "flex-end" : "flex-start",
              }}
            >
              {msg.role === "bot" && <div style={styles.botAvatar}>🎓</div>}
              <div
                style={
                  msg.role === "user" ? styles.userBubble : styles.botBubble
                }
              >
                {msg.role === "bot" ? (
                  <ReactMarkdown
                    components={{
                      p: ({ children }) => <p style={{ margin: "0 0 8px 0" }}>{children}</p>,
                      a: ({ href, children }) => (
                        <a href={href} target="_blank" rel="noopener noreferrer" style={{ color: UPOU_GREEN, textDecoration: "underline" }}>
                          {children}
                        </a>
                      ),
                      ul: ({ children }) => <ul style={{ margin: "4px 0", paddingLeft: "20px" }}>{children}</ul>,
                      li: ({ children }) => <li style={{ marginBottom: "4px" }}>{children}</li>,
                      strong: ({ children }) => <strong style={{ color: UPOU_DARK }}>{children}</strong>,
                    }}
                  >
                    {msg.text}
                  </ReactMarkdown>
                ) : (
                  msg.text
                )}
              </div>
            </div>
          ))}

          {loading && (
            <div style={{ ...styles.messageBubbleWrap, justifyContent: "flex-start" }}>
              <div style={styles.botAvatar}>🎓</div>
              <div style={styles.botBubble}>
                <div style={styles.typingDots}>
                  <span style={styles.dot}>●</span>
                  <span style={{ ...styles.dot, animationDelay: "0.2s" }}>●</span>
                  <span style={{ ...styles.dot, animationDelay: "0.4s" }}>●</span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Quick Questions */}
        {messages.length <= 1 && (
          <div style={styles.quickQuestions}>
            {quickQuestions.map((q, i) => (
              <button
                key={i}
                style={styles.quickBtn}
                onClick={() => {
                  setInput(q);
                  setTimeout(() => {
                    setInput(q);
                    const fakeEvent = { key: "Enter", shiftKey: false, preventDefault: () => {} };
                    // Trigger send directly
                  }, 0);
                  setInput("");
                  setMessages((prev) => [...prev, { role: "user", text: q }]);
                  setLoading(true);
                  sendQuery(q)
                    .then((response) => {
                      setMessages((prev) => [...prev, { role: "bot", text: response }]);
                    })
                    .catch(() => {
                      setMessages((prev) => [
                        ...prev,
                        { role: "bot", text: "Sorry, something went wrong." },
                      ]);
                    })
                    .finally(() => setLoading(false));
                }}
                onMouseEnter={(e) => {
                  e.target.style.background = UPOU_GREEN;
                  e.target.style.color = "#fff";
                }}
                onMouseLeave={(e) => {
                  e.target.style.background = "#fff";
                  e.target.style.color = UPOU_GREEN;
                }}
              >
                {q}
              </button>
            ))}
          </div>
        )}

        {/* Input Area */}
        <div style={styles.inputArea}>
          <input
            style={styles.input}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about UPOU admissions..."
            disabled={loading}
          />
          <button
            style={{
              ...styles.sendBtn,
              opacity: loading || !input.trim() ? 0.5 : 1,
              cursor: loading || !input.trim() ? "not-allowed" : "pointer",
            }}
            onClick={handleSend}
            disabled={loading || !input.trim()}
          >
            {loading ? "..." : "Send"}
          </button>
        </div>
      </main>

      {/* Footer */}
      <footer style={styles.footer}>
        <p>Powered by UPOU Admissions Knowledge Base • IS 215 Project</p>
      </footer>

      <style>{`
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Inter', -apple-system, sans-serif; background: ${UPOU_LIGHT_BG}; }
        @keyframes pulse {
          0%, 100% { opacity: 0.3; }
          50% { opacity: 1; }
        }
        input:focus { outline: none; border-color: ${UPOU_GREEN} !important; box-shadow: 0 0 0 3px rgba(138,21,56,0.15); }
        button:active { transform: scale(0.97); }
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #ccc; border-radius: 3px; }
      `}</style>
    </div>
  );
}

const styles = {
  page: {
    display: "flex",
    flexDirection: "column",
    height: "100vh",
    maxWidth: "900px",
    margin: "0 auto",
    background: "#fff",
    boxShadow: "0 0 40px rgba(0,0,0,0.08)",
  },
  header: {
    background: `linear-gradient(135deg, ${UPOU_GREEN} 0%, ${UPOU_DARK} 100%)`,
    padding: "16px 24px",
    color: "#fff",
  },
  headerInner: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
  },
  logoArea: {
    display: "flex",
    alignItems: "center",
    gap: "14px",
  },
  logoCircle: {
    width: "48px",
    height: "48px",
    borderRadius: "50%",
    background: "rgba(255,255,255,0.2)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    border: "2px solid rgba(255,255,255,0.4)",
  },
  logoText: {
    fontWeight: "700",
    fontSize: "18px",
    letterSpacing: "1px",
  },
  title: {
    fontSize: "20px",
    fontWeight: "700",
    margin: 0,
    letterSpacing: "-0.3px",
  },
  subtitle: {
    fontSize: "12px",
    opacity: 0.8,
    margin: 0,
    marginTop: "2px",
  },
  statusBadge: {
    display: "flex",
    alignItems: "center",
    gap: "6px",
    fontSize: "13px",
    background: "rgba(255,255,255,0.15)",
    padding: "6px 14px",
    borderRadius: "20px",
  },
  statusDot: {
    width: "8px",
    height: "8px",
    borderRadius: "50%",
    background: "#4ADE80",
    display: "inline-block",
  },
  chatContainer: {
    flex: 1,
    display: "flex",
    flexDirection: "column",
    overflow: "hidden",
  },
  messagesArea: {
    flex: 1,
    overflowY: "auto",
    padding: "24px",
    display: "flex",
    flexDirection: "column",
    gap: "16px",
  },
  messageBubbleWrap: {
    display: "flex",
    alignItems: "flex-start",
    gap: "10px",
  },
  botAvatar: {
    width: "36px",
    height: "36px",
    borderRadius: "50%",
    background: `linear-gradient(135deg, ${UPOU_GREEN}, ${UPOU_DARK})`,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontSize: "18px",
    flexShrink: 0,
  },
  userBubble: {
    background: `linear-gradient(135deg, ${UPOU_GREEN}, ${UPOU_DARK})`,
    color: "#fff",
    padding: "12px 18px",
    borderRadius: "20px 20px 4px 20px",
    maxWidth: "75%",
    fontSize: "14px",
    lineHeight: "1.55",
    boxShadow: "0 2px 8px rgba(138,21,56,0.15)",
  },
  botBubble: {
    background: UPOU_LIGHT_BG,
    color: "#1a1a1a",
    padding: "14px 18px",
    borderRadius: "20px 20px 20px 4px",
    maxWidth: "75%",
    fontSize: "14px",
    lineHeight: "1.6",
    border: "1px solid #e5e7e5",
    boxShadow: "0 1px 4px rgba(0,0,0,0.04)",
  },
  typingDots: {
    display: "flex",
    gap: "4px",
  },
  dot: {
    animation: "pulse 1s infinite",
    color: UPOU_GREEN,
    fontSize: "14px",
  },
  quickQuestions: {
    display: "flex",
    flexWrap: "wrap",
    gap: "8px",
    padding: "0 24px 16px",
  },
  quickBtn: {
    background: "#fff",
    color: UPOU_GREEN,
    border: `1.5px solid ${UPOU_GREEN}`,
    borderRadius: "20px",
    padding: "8px 16px",
    fontSize: "13px",
    cursor: "pointer",
    transition: "all 0.2s",
    fontFamily: "inherit",
    fontWeight: "500",
  },
  inputArea: {
    padding: "16px 24px",
    borderTop: "1px solid #e5e7e5",
    display: "flex",
    gap: "12px",
    background: "#fff",
  },
  input: {
    flex: 1,
    padding: "14px 18px",
    borderRadius: "12px",
    border: "1.5px solid #d1d5d1",
    fontSize: "14px",
    fontFamily: "inherit",
    transition: "border-color 0.2s, box-shadow 0.2s",
  },
  sendBtn: {
    background: `linear-gradient(135deg, ${UPOU_GREEN}, ${UPOU_DARK})`,
    color: "#fff",
    border: "none",
    borderRadius: "12px",
    padding: "14px 28px",
    fontSize: "14px",
    fontWeight: "600",
    fontFamily: "inherit",
    cursor: "pointer",
    transition: "all 0.2s",
    letterSpacing: "0.3px",
  },
  footer: {
    textAlign: "center",
    padding: "12px",
    fontSize: "12px",
    color: "#888",
    borderTop: "1px solid #e5e7e5",
  },
};

export default App;