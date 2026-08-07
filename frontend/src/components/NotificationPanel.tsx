"use client";

import React from "react";

export interface Notification {
  id: string;
  event: string;
  channel: string;
  status: "sent" | "mock" | "failed";
  rendered: string;
  timestamp: string;
}

export function NotificationPanel({ notifications }: { notifications: Notification[] }) {
  if (notifications.length === 0) return null;

  return (
    <div style={{ borderTop: "1px solid #e0e0e0", padding: "1rem", background: "#fafafa" }}>
      <h3 style={{ fontSize: "0.85rem", fontWeight: 600, marginBottom: "0.75rem", color: "#666" }}>
        Notifications
      </h3>
      <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
        {notifications.map((n) => (
          <div
            key={n.id}
            style={{
              border: "1px solid #e0e0e0",
              borderRadius: 6,
              padding: "0.75rem",
              background: "#fff",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.5rem" }}>
              <span style={{ fontSize: "0.8rem", fontWeight: 500 }}>
                {n.event.replace(/_/g, " ")}
              </span>
              <StatusBadge status={n.status} channel={n.channel} />
            </div>
            <div
              style={{ fontSize: "0.8rem", color: "#555", lineHeight: 1.5 }}
              dangerouslySetInnerHTML={{ __html: sanitize(n.rendered) }}
            />
          </div>
        ))}
      </div>
    </div>
  );
}

function StatusBadge({ status, channel }: { status: string; channel: string }) {
  const colors: Record<string, { bg: string; text: string }> = {
    sent: { bg: "#e8f5e9", text: "#2e7d32" },
    mock: { bg: "#fff3e0", text: "#e65100" },
    failed: { bg: "#fdecea", text: "#d32f2f" },
  };
  const c = colors[status] ?? colors.mock;

  return (
    <span
      style={{
        fontSize: "0.7rem",
        padding: "0.15rem 0.5rem",
        borderRadius: 10,
        background: c.bg,
        color: c.text,
        fontWeight: 500,
      }}
    >
      {channel} · {status}
    </span>
  );
}

function sanitize(html: string): string {
  return html
    .replace(/<script[^>]*>[\s\S]*?<\/script>/gi, "")
    .replace(/on\w+="[^"]*"/gi, "");
}
