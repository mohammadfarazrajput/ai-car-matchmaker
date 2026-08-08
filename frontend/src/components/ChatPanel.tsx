"use client";

import React, { useState, useRef, useCallback } from "react";
import { useA2UI } from "@/lib/a2ui/a2ui-provider";
import { SurfaceRenderer } from "@/lib/a2ui/renderer";
import { consumeAGUIStream, AGUIEvent } from "@/lib/a2ui/ag-ui-stream";
import { NotificationPanel, Notification } from "./NotificationPanel";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  text?: string;
  surfaces?: string[];
}

export function ChatPanel() {
  const { surfaces, applyFrame, clear } = useA2UI();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const sessionIdRef = useRef<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  const sendMessage = useCallback(async () => {
    const text = input.trim();
    if (!text || isLoading) return;

    setInput("");
    setError(null);

    const userMsg: ChatMessage = { id: `u-${Date.now()}`, role: "user", text };
    setMessages((prev) => [...prev, userMsg]);

    const assistantMsg: ChatMessage = {
      id: `a-${Date.now()}`,
      role: "assistant",
      surfaces: [],
    };
    setMessages((prev) => [...prev, assistantMsg]);

    setIsLoading(true);

    try {
      const body: Record<string, unknown> = {
        messages: [{ role: "user", content: text }],
      };
      if (sessionIdRef.current) {
        body.session_id = sessionIdRef.current;
      }

      const res = await fetch(`${API_URL}/agent`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }

      let textBuffer = "";

      await consumeAGUIStream(res, {
        onEvent: (event: AGUIEvent) => {
          if (event.sessionId && !sessionIdRef.current) {
            sessionIdRef.current = event.sessionId;
          }
        },
        onText: (content: string) => {
          textBuffer += content;
          setMessages((prev) => {
            const updated = [...prev];
            const last = updated[updated.length - 1];
            if (last && last.role === "assistant") {
              updated[updated.length - 1] = { ...last, text: textBuffer };
            }
            return updated;
          });
          scrollToBottom();
        },
        onFrame: (frame) => {
          applyFrame(frame);
          setMessages((prev) => {
            const updated = [...prev];
            const last = updated[updated.length - 1];
            if (last && last.role === "assistant") {
              const surfaces = last.surfaces ?? [];
              const surfaceId = frame.createSurface?.surfaceId ?? frame.updateComponents?.surfaceId;
              if (surfaceId && !surfaces.includes(surfaceId)) {
                updated[updated.length - 1] = { ...last, surfaces: [...surfaces, surfaceId] };
              }
            }
            return updated;
          });
          scrollToBottom();
        },
        onState: (state) => {
          if (Array.isArray(state.notifications)) {
            setNotifications(state.notifications);
          }
        },
        onError: (err) => {
          setError(err);
        },
      });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Connection failed");
    } finally {
      setIsLoading(false);
      scrollToBottom();
    }
  }, [input, isLoading, applyFrame, scrollToBottom]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%", border: "1px solid #e0e0e0", borderRadius: 8, overflow: "hidden" }}>
      <div style={{ padding: "0.75rem 1rem", borderBottom: "1px solid #e0e0e0", background: "#fafafa", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <span style={{ fontWeight: 600 }}>AI Car Matchmaker</span>
        <button
          onClick={() => { clear(); setMessages([]); sessionIdRef.current = null; }}
          style={{ fontSize: "0.8rem", padding: "0.25rem 0.5rem", border: "1px solid #ccc", borderRadius: 4, background: "#fff", cursor: "pointer" }}
        >
          New chat
        </button>
      </div>

      <div style={{ flex: 1, overflowY: "auto", padding: "1rem" }}>
        {messages.length === 0 && (
          <div style={{ textAlign: "center", color: "#999", marginTop: "2rem" }}>
            <p style={{ fontSize: "1.1rem", marginBottom: "0.5rem" }}>What kind of car are you looking for?</p>
            <p style={{ fontSize: "0.85rem" }}>Tell me your intent, category, budget, and when you need it.</p>
          </div>
        )}

        {messages.map((msg) => (
          <div key={msg.id} style={{ marginBottom: "1rem" }}>
            {msg.role === "user" ? (
              <div style={{ display: "flex", justifyContent: "flex-end" }}>
                <div style={{ background: "#1a1a1a", color: "#fff", padding: "0.5rem 1rem", borderRadius: 12, maxWidth: "70%" }}>
                  {msg.text}
                </div>
              </div>
            ) : (
              <div>
                {msg.text && (
                  <div style={{ background: "#f5f5f5", padding: "0.5rem 1rem", borderRadius: 12, maxWidth: "70%", whiteSpace: "pre-wrap" }}>
                    {msg.text}
                  </div>
                )}
                {msg.surfaces?.map((surfaceId) => {
                  const surface = surfaces.find((s) => s.surfaceId === surfaceId);
                  if (!surface) return null;
                  return (
                    <div key={surfaceId} style={{ marginTop: "0.5rem" }}>
                      <SurfaceRenderer surface={surface} />
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        ))}

        {isLoading && messages[messages.length - 1]?.text === undefined && (
          <div style={{ display: "flex", gap: 4, padding: "0.5rem 1rem" }}>
            <span style={{ animation: "pulse 1.4s infinite" }}>●</span>
            <span style={{ animation: "pulse 1.4s infinite 0.2s" }}>●</span>
            <span style={{ animation: "pulse 1.4s infinite 0.4s" }}>●</span>
          </div>
        )}

        {error && (
          <div style={{ color: "#d32f2f", background: "#fdecea", padding: "0.5rem 1rem", borderRadius: 8, marginTop: "0.5rem", fontSize: "0.85rem" }}>
            {error}
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <NotificationPanel notifications={notifications} />

      <div style={{ padding: "0.75rem 1rem", borderTop: "1px solid #e0e0e0", display: "flex", gap: "0.5rem" }}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Describe what you need..."
          disabled={isLoading}
          style={{ flex: 1, padding: "0.5rem 1rem", borderRadius: 8, border: "1px solid #ccc", fontSize: "0.95rem" }}
        />
        <button
          onClick={sendMessage}
          disabled={isLoading || !input.trim()}
          style={{
            padding: "0.5rem 1.25rem",
            borderRadius: 8,
            border: "none",
            background: input.trim() ? "#1a1a1a" : "#ccc",
            color: "#fff",
            cursor: input.trim() ? "pointer" : "not-allowed",
            fontWeight: 600,
          }}
        >
          Send
        </button>
      </div>
    </div>
  );
}
