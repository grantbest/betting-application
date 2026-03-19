"use client";

import { useState, useEffect, useRef } from "react";
import { Send, Bot, LayoutDashboard, Activity, MessageSquare } from "lucide-react";
import Link from "next/link";

export default function ChatPage() {
  const [messages, setMessages] = useState<any[]>([]);
  const [input, setInput] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);

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
        body: JSON.stringify({ role: "user", content }),
      });
      fetchMessages();
    } catch (e) {}
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-50 flex flex-col font-sans">

      {/* Header */}
      <header className="sticky top-0 z-10 px-5 py-4 border-b border-slate-800 bg-slate-950/80 backdrop-blur-sm flex justify-between items-center">
        <div className="flex items-center gap-3">
          <div className="bg-emerald-500/10 p-2 rounded-xl">
            <MessageSquare size={20} className="text-emerald-400" />
          </div>
          <div>
            <h1 className="text-sm font-black tracking-tight">BestFam Agent</h1>
            <p className="text-[10px] text-slate-500 uppercase font-bold">Secure Mobile Bridge</p>
          </div>
        </div>
        <div className="flex gap-3">
          <Link href="/health" className="text-slate-500 hover:text-slate-300 transition-colors">
            <Activity size={20} />
          </Link>
          <Link href="/" className="text-slate-500 hover:text-slate-300 transition-colors">
            <LayoutDashboard size={20} />
          </Link>
        </div>
      </header>

      {/* Messages */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto px-5 py-5 flex flex-col gap-4">
        {messages.length === 0 && (
          <div className="flex-1 flex flex-col items-center justify-center opacity-30 py-24">
            <Bot size={48} />
            <p className="text-xs mt-3 font-bold">System ready. How can I help?</p>
          </div>
        )}
        {messages.map((m: any) => (
          <div key={m.message_id} className={`flex w-full ${m.role === "user" ? "justify-end" : "justify-start"}`}>
            <div className={`max-w-[85%] px-4 py-3 text-sm leading-relaxed shadow-lg ${
              m.role === "user"
                ? "bg-blue-600 rounded-[20px_20px_4px_20px]"
                : "bg-slate-800 rounded-[20px_20px_20px_4px]"
            }`}>
              {m.content}
            </div>
          </div>
        ))}
      </div>

      {/* Input */}
      <div className="sticky bottom-0 px-5 py-4 border-t border-slate-800 bg-slate-950 flex gap-3">
        <input
          className="flex-1 bg-slate-900 border border-slate-700 rounded-full px-5 py-3 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors"
          placeholder="Message BestFam Agent..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
        />
        <button
          onClick={sendMessage}
          className="bg-emerald-500 hover:bg-emerald-400 transition-colors rounded-full w-11 h-11 flex items-center justify-center shrink-0"
        >
          <Send size={18} className="text-white" />
        </button>
      </div>

    </div>
  );
}
