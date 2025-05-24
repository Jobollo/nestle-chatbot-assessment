import React, { useState } from "react";

export default function Chatbot() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSend = async () => {
    if (!input.trim()) return;
    setError("");
    const userMsg = { sender: "user", text: input };
    setMessages((msgs) => [...msgs, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch("https://nestle-bot-backend-123.azurewebsites.net/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: userMsg.text }),
      });
      if (!res.ok) throw new Error("Failed to fetch");
      const data = await res.json();
      setMessages((msgs) => [...msgs, { sender: "bot", text: data.answer }]);
    } catch (e) {
      setMessages((msgs) => [
        ...msgs,
        { sender: "bot", text: "Sorry, I couldn't reach the server." },
      ]);
      setError("Failed to fetch");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        position: "fixed",
        bottom: 32,
        right: 32,
        zIndex: 1001,
        width: open ? 350 : 64,
        height: open ? 500 : 64,
        transition: "all 0.2s",
      }}
    >
      {!open && (
        <button
          onClick={() => setOpen(true)}
          style={{
            width: 64,
            height: 64,
            borderRadius: "50%",
            border: "none",
            background: "#fff",
            boxShadow: "0 2px 8px rgba(0,0,0,0.12)",
            cursor: "pointer",
            padding: 0,
          }}
        >
          <img
            src="/chatbot_icon.png"
            alt="Chatbot"
            style={{
              width: 48,
              height: 48,
              objectFit: "contain",
              display: "block",
              margin: "0 auto",
            }}
          />
        </button>
      )}
      {open && (
        <div
          style={{
            width: 350,
            height: 500,
            background: "#fff",
            borderRadius: 20,
            boxShadow: "0 6px 24px rgba(0,0,0,0.15)",
            display: "flex",
            flexDirection: "column",
            overflow: "hidden",
          }}
        >
          <div
            style={{
              padding: 12,
              borderBottom: "1px solid #eee",
              background: "#f3f6fa",
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
            }}
          >
            <span>
              <b>Made with Nestlé Assistant</b>
            </span>
            <button
              onClick={() => setOpen(false)}
              style={{
                border: "none",
                background: "transparent",
                fontSize: 22,
                cursor: "pointer",
                marginLeft: 12,
                color: "#888",
              }}
            >
              ×
            </button>
          </div>
          <div
            style={{
              flex: 1,
              overflowY: "auto",
              padding: 12,
              background: "#f9fbfd",
            }}
          >
            {messages.map((m, i) => (
              <div
                key={i}
                style={{
                  margin: "8px 0",
                  textAlign: m.sender === "user" ? "right" : "left",
                }}
              >
                <span
                  style={{
                    display: "inline-block",
                    padding: "8px 14px",
                    borderRadius: 16,
                    background: m.sender === "user" ? "#ddeafc" : "#eaeaea",
                    whiteSpace: "pre-line"
                  }}
                >
                  {m.text}
                </span>
              </div>
            ))}
            {loading && (
              <div style={{ fontStyle: "italic", color: "#aaa" }}>
                Thinking...
              </div>
            )}
            {error && (
              <div style={{ color: "red", marginTop: 8, fontSize: 13 }}>
                ERROR
                <br />
                {error}
              </div>
            )}
          </div>
          <div
            style={{
              padding: 10,
              borderTop: "1px solid #eee",
              background: "#f3f6fa",
              display: "flex",
              alignItems: "center",
            }}
          >
            <input
              style={{
                flex: 1,
                padding: 8,
                borderRadius: 8,
                border: "1px solid #ccc",
                outline: "none",
                marginRight: 6,
                fontSize: 15,
              }}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") handleSend();
              }}
              disabled={loading}
              placeholder="Ask a question..."
              autoFocus
            />
            <button
              onClick={handleSend}
              disabled={loading || !input.trim()}
              style={{
                padding: "8px 16px",
                borderRadius: 8,
                border: "none",
                background: "#459cff",
                color: "#fff",
                cursor: loading ? "not-allowed" : "pointer",
                fontWeight: 600,
              }}
            >
              Send
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
