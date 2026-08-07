import { ChatPanel } from "@/components/ChatPanel";

export default function Home() {
  return (
    <main
      style={{
        display: "flex",
        flexDirection: "column",
        height: "100vh",
        maxWidth: 800,
        margin: "0 auto",
        padding: "1rem",
        fontFamily: "system-ui, -apple-system, sans-serif",
      }}
    >
      <ChatPanel />
      <p style={{ textAlign: "center", fontSize: "0.7rem", color: "#aaa", marginTop: "0.5rem" }}>
        Synthetic dataset · Simulated transactions only
      </p>
    </main>
  );
}
