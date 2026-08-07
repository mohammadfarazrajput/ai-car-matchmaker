# Amulate Summer Hackathon 2026 - AI Car Matchmaker Architecture

## Executive Overview
This platform is an interactive, multi-step AI-driven car matchmaking system built for the **Amulate Summer Hackathon 2026 (Hosted by BMW)**. The application seamlessly bridges interactive Generative UI (A2UI), protocol-based MCP tool integration (MCP Apps), and external multi-channel outreach infrastructure (Twilio Voice, Twilio SMS, SendGrid Email, and Slack).

---

## 1. Core Architectural Pillars

```
+-----------------------------------------------------------------------------------+
|                                  USER INTERFACE                                   |
|       Generative UI (A2UI Dynamic Client)  <--->  Embedded MCP Webview Apps       |
+------------------------------------------+----------------------------------------+
                                           |
                                           v
+-----------------------------------------------------------------------------------+
|                             MULTISTEP AGENT ENGINE                                |
|        (State Orchestration: INTERVIEW -> RESEARCH -> RANKING -> CHECKOUT)        |
+-------------------+----------------------+-------------------+--------------------+
                    |                      |                   |
                    v                      v                   v
+-----------------------+  +-----------------------+  +-----------------------------+
|    MCP TOOL SERVER    |  |  MOCK MARKETPLACE API |  |   OUTBOUND / ENGAGEMENT     |
| - Form App            |  | - 100+ Listings       |  |   INFRASTRUCTURE SERVICES   |
| - Checkout App        |  | - 10 Categories       |  | - Twilio Voice Agent        |
| - Inventory Search    |  | - 10 Brands/Category  |  | - Twilio SMS Engine         |
+-----------------------+  +-----------------------+  | - SendGrid Email Engine     |
                                                      | - Slack Sales Operations    |
                                                      +-----------------------------+
```

### Protocol & Framework Matrix
| Domain | Component / Technology | Purpose |
| :--- | :--- | :--- |
| **Agent Core** | Claude Agent SDK / LangChain / OpenAI SDK | State management, tool calling, reasoning execution |
| **Frontend UI** | A2UI Protocol (Agent-to-UI) | Dynamic visual streaming (progress, chips, cards, sliders) |
| **Form & Checkout** | Model Context Protocol (MCP) Apps | In-chat interactive web apps for data capture & safe mock payment |
| **Mock Database** | SQLite / JSON Dataset | 100+ listings across 10 categories & 10 brands (inc. BMW) |
| **Outbound Voice** | Twilio Voice + Deepgram STT + Whisper | Interactive voice calls, phone intake, AI follow-ups |
| **Outbound Messaging**| Twilio SMS | Deal alerts, instant booking links, status updates |
| **Outbound Email** | SendGrid | Rich HTML vehicle dossiers, comparison reports, payment receipts |
| **Internal Operations**| Slack Webhooks / Slack Bot | Instant high-intent lead alerts to sales reps & command overrides |
| **Observability** | Langfuse / Arize Phoenix (OTel) | Multistep trace evaluation, tool call monitoring, latency tracking |

---

## 2. Directory & Documentation Index

The platform documentation is organized into focused, modular design specifications:

1. **[System Architecture & Data Flow (`docs/SYSTEM_ARCHITECTURE.md`)](./SYSTEM_ARCHITECTURE.md)**: Full agent state machine, A2UI protocol spec, and dataset schema.
2. **[Voice & Calling Strategy (`docs/VOICE_CALLING_PLAN.md`)](./VOICE_CALLING_PLAN.md)**: Twilio Voice, Deepgram STT, and Whisper pipeline for phone discovery & voice follow-ups.
3. **[SMS Messaging Strategy (`docs/SMS_MESSAGING_PLAN.md`)](./SMS_MESSAGING_PLAN.md)**: Twilio SMS integration triggers, alert templates, and two-way SMS workflows.
4. **[Email Communication Strategy (`docs/EMAIL_COMMUNICATION_PLAN.md`)](./EMAIL_COMMUNICATION_PLAN.md)**: SendGrid template designs, PDF dossier generation, and automated follow-up cadences.
5. **[Slack Sales Operations (`docs/SLACK_OPERATIONS_PLAN.md`)](./SLACK_OPERATIONS_PLAN.md)**: High-intent lead routing, sales rep overrides, and internal command bot specs.
6. **[Hackathon Execution Roadmap (`docs/HACKATHON_ROADMAP.md`)](./HACKATHON_ROADMAP.md)**: Phase-by-phase implementation schedule, evaluation checklist, and submission guidelines.
