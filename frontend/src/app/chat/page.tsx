
"use client";

import { useState, useEffect, useRef } from "react";
import { Send, User, Bot, LayoutDashboard, Activity, MessageSquare } from "lucide-react";
import Link from "next/link";

const S: any = {
  container: { minHeight: "100vh", backgroundColor: "#020617", color: "#f8fafc", display: "flex", flexDirection: "column", fontFamily: "sans-serif" },
  header: { padding: "20px", borderBottom: "1px solid #1e293b", display: "flex", justifyContent: "space-between", alignItems: "center", backgroundColor: "rgba(15, 23, 42, 0.8)", backdropFilter: "blur(10px)", position: "sticky", top: 0, zIndex: 10 },
  chatArea: { flex: 1, padding: "20px", overflowY: "auto", display: "flex", flexDirection: "column", gap: "16px" },
  msgRow: (isUser: boolean) => ({ display: "flex", justifyContent: isUser ? "flex-end" : "flex-start", width: "100%" }),
  bubble: (isUser: boolean) => ({ maxWidth: "85%", padding: "12px 16px", borderRadius: isUser ? "20px 20px 4px 20px" : "20px 20px 20px 4px", backgroundColor: isUser ? "#3b82f6" : "#1e293b", color: "#fff", fontSize: "14px", lineHeight: "1.5", boxShadow: "0 4px 12px rgba(0,0,0,0.1)" }),
  inputArea: { padding: "20px", borderTop: "1px solid #1e293b", display: "flex", gap: "12px", backgroundColor: "#020617", position: "sticky", bottom: 0 },
  input: { flex: 1, backgroundColor: "#0f172a", border: "1px solid #1e293b", borderRadius: "99px", padding: "12px 20px", color: "#fff", fontSize: "14px", outline: "none" },
  sendBtn: { backgroundColor: "#10b981", border: "none", borderRadius: "50%", width: "44px", height: "44px", display: "flex", alignItems: "center", justifyContent: "center", cursor: "pointer", color: "#fff" }
};

export default function ChatPage() {
  const [messages, setMessages] = useState<any[]>([]);
  const [input, setInput] = useState("");
  const scrollRef = useRef<any>(null);

  const fetchMessages = async () => {
    try {
      const res = await fetch("/api/chat");
      const data = await res.json();
      setMessages(data);
    } catch (e) {}
  };

  useEffect(() => {
    fetchMessages();
    const i = setInterval(fetchMessages, 3000);
    return () => clearInterval(i);
  }, []);

  useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;
    const content = input;
    setInput("");
    try {
      await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ role: "user", content })
      });
      fetchMessages();
    } catch (e) {}
  };

  return (
    <div style={S.container}>
      <header style={S.header}>
        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <div style={{ backgroundColor: "#10b98122", padding: "8px", borderRadius: "12px" }}>
            <MessageSquare size={20} color="#10b981" />
          </div>
          <div>
            <h1 style={{ fontSize: "16px", fontWeight: "900", margin: 0, letterSpacing: "-0.5px" }}>BestFam Agent</h1>
            <p style={{ fontSize: "10px", color: "#64748b", margin: 0, textTransform: "uppercase", fontWeight: 700 }}>Secure Mobile Bridge</p>
          </div>
        </div>
        <div style={{ display: "flex", gap: "8px" }}>
          <Link href="/health" style={{ color: "#64748b" }}><Activity size={20} /></Link>
          <Link href="/" style={{ color: "#64748b" }}><LayoutDashboard size={20} /></Link>
        </div>
      </header>

      <div style={S.chatArea} ref={scrollRef}>
        {messages.length === 0 && (
          <div style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", opacity: 0.3 }}>
            <Bot size={48} />
            <p style={{ fontSize: "12px", marginTop: "12px", fontWeight: "700" }}>System ready. How can I help?</p>
          </div>
        )}
        {messages.map((m: any) => (
          <div key={m.message_id} style={S.msgRow(m.role === "user")}>
            <div style={S.bubble(m.role === "user")}>{m.content}</div>
          </div>
        ))}
      </div>

      <div style={S.inputArea}>
        <input 
          style={S.input} 
          placeholder="Message BestFam Agent..." 
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
        />
        <button style={S.sendBtn} onClick={sendMessage}>
          <Send size={18} />
        </button>
      </div>
    </div>
  );
}
