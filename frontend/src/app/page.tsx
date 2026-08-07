export default function Home() {
  return (
    <main
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        minHeight: "100vh",
        padding: "2rem",
        fontFamily: "system-ui, -apple-system, sans-serif",
      }}
    >
      <h1 style={{ fontSize: "2rem", marginBottom: "0.5rem" }}>AI Car Matchmaker</h1>
      <p style={{ color: "#666", marginBottom: "1rem" }}>
        Amulate Summer Hackathon 2026 — hosted by BMW
      </p>
      <p style={{ maxWidth: "32rem", textAlign: "center", color: "#888" }}>
        Open the sidebar to start a conversation. The agent will interview you about what
        you need, research the marketplace, and present ranked suggestions — all within
        the chat.
      </p>
      <p style={{ marginTop: "1.5rem", fontSize: "0.8rem", color: "#aaa" }}>
        Synthetic dataset. Simulated transactions only.
      </p>
    </main>
  );
}
