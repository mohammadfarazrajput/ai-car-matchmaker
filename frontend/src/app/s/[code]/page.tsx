"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface ResumeResult {
  ok: boolean;
  session_id?: string;
  error?: string;
  message?: string;
  start_fresh_url?: string;
}

export default function ResumePage() {
  const params = useParams();
  const router = useRouter();
  const code = params.code as string;
  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");
  const [result, setResult] = useState<ResumeResult | null>(null);

  useEffect(() => {
    if (!code) return;

    fetch(`${API_URL}/s/${code}`, { redirect: "manual" })
      .then((res) => {
        if (res.status === 302 || res.status === 301) {
          const location = res.headers.get("location");
          if (location) {
            window.location.href = location;
            return;
          }
        }
        if (res.status === 410) {
          return res.json().then((data) => {
            setResult(data);
            setStatus("error");
          });
        }
        if (res.ok) {
          setStatus("success");
        } else {
          setStatus("error");
          setResult({ ok: false, error: `HTTP ${res.status}` });
        }
      })
      .catch((err) => {
        setStatus("error");
        setResult({ ok: false, error: err.message });
      });
  }, [code]);

  if (status === "loading") {
    return (
      <main style={{ display: "flex", alignItems: "center", justifyContent: "center", minHeight: "100vh" }}>
        <p>Resuming session…</p>
      </main>
    );
  }

  if (status === "success") {
    return (
      <main style={{ display: "flex", alignItems: "center", justifyContent: "center", minHeight: "100vh" }}>
        <p>Session restored. Redirecting…</p>
      </main>
    );
  }

  return (
    <main
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        minHeight: "100vh",
        padding: "2rem",
        fontFamily: "system-ui, sans-serif",
      }}
    >
      <h1 style={{ fontSize: "1.5rem", marginBottom: "1rem" }}>Session unavailable</h1>
      <p style={{ color: "#666", marginBottom: "0.5rem", maxWidth: "30rem", textAlign: "center" }}>
        {result?.message ?? "This resume link is no longer valid."}
      </p>
      {result?.error && (
        <p style={{ fontSize: "0.8rem", color: "#999", marginBottom: "1.5rem" }}>
          Reason: {result.error}
        </p>
      )}
      <button
        onClick={() => router.push("/")}
        style={{
          padding: "0.6rem 1.5rem",
          borderRadius: 8,
          border: "none",
          background: "#1a1a1a",
          color: "#fff",
          cursor: "pointer",
          fontWeight: 600,
        }}
      >
        Start a new conversation
      </button>
    </main>
  );
}
