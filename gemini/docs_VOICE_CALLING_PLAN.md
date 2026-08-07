# Voice Communication & Call Plan (Twilio Voice + Deepgram + Whisper)

## 1. Strategic Purpose & Placement
Voice interactions provide high-touch engagement for car buyers who prefer phone consultations or require immediate follow-up when high-intent buying signals are triggered.

```
+------------------+         +------------------+         +------------------+
| Inbound Phone    |  ---->  | Twilio Voice     |  ---->  | Deepgram STT     |
| Customer Call    |         | Webhook Gateway  |         | (Real-time)      |
+------------------+         +------------------+         +---------+--------+
                                                                    |
                                                                    v
+------------------+         +------------------+         +------------------+
| Twilio TTS /     |  <----  | Multistep Agent  |  <----  | Whisper          |
| Audio Streaming  |         | Decision Engine  |         | (Deep Transcript)|
+------------------+         +------------------+         +------------------+
```

---

## 2. Technical Capabilities & Integration Map

### A. Inbound Voice Interview Concierge
* **Trigger:** Customer calls dedicated Twilio phone number.
* **Flow:**
  1. Twilio Voice connects stream to **Deepgram Speech-to-Text** (sub-300ms latency).
  2. Agent processes voice transcript and extracts structured variables (`budget`, `category`, `lease vs purchase`).
  3. Response rendered via high-quality Text-to-Speech (TTS) back through Twilio Voice.
  4. Conversation state saved directly into user session for web sync.

### B. Outbound Test-Drive Follow-Up Agent
* **Trigger:** User completes Checkout MCP App in chat for high-value model (e.g., BMW i4 or X5).
* **Execution:**
  1. System queues automated Twilio outbound call 15 minutes post-checkout.
  2. AI agent confirms test-drive appointment details and preferred dealership location.
  3. If user requests human assistance, Twilio performs a warm call transfer to the dealer sales line.

---

## 3. Implementation Verification Checklist
- [ ] Validated Twilio Voice Webhook endpoint configuration (`/api/voice/inbound`).
- [ ] Confirmed Deepgram API key & WebSocket stream connection.
- [ ] Verified Whisper fallback transcript extraction for noisy voice calls.
- [ ] Tested safe call transfer logic when human agent escalation is triggered.
