# Amulate Summer Hackathon 2026 - Execution Roadmap

## Phase Schedule & Task Breakdown

```
+-----------------------------------------------------------------------------------+
|  PHASE 1: Foundations & Spec Setup                                                 |
|  - Initialize spec-kit, directory architecture, and mock dataset (100+ listings)  |
+-----------------------------------------------------------------------------------+
                                           |
                                           v
+-----------------------------------------------------------------------------------+
|  PHASE 2: Multistep Agent Core & MCP Tool Servers                                  |
|  - Implement Agent State Machine (Interview -> Research -> Rank -> Checkout)       |
|  - Build MCP Form App & MCP Mock Checkout App                                      |
+-----------------------------------------------------------------------------------+
                                           |
                                           v
+-----------------------------------------------------------------------------------+
|  PHASE 3: Generative UI (A2UI Protocol Client)                                    |
|  - Implement A2UI dynamic component renderer in frontend Web app                   |
+-----------------------------------------------------------------------------------+
                                           |
                                           v
+-----------------------------------------------------------------------------------+
|  PHASE 4: Outbound Service Integrations (Twilio, SendGrid, Slack)                 |
|  - Deploy Voice, SMS, Email, and Slack operational flows                           |
+-----------------------------------------------------------------------------------+
                                           |
                                           v
+-----------------------------------------------------------------------------------+
|  PHASE 5: Observability, Packaging & Submission                                    |
|  - Add Langfuse/Arize Phoenix OpenTelemetry tracing                               |
|  - Dockerize full stack, produce 3-min video demo & pitch deck                     |
+-----------------------------------------------------------------------------------+
```

---

## Final Submission Verification Matrix
- [x] **Spec-Driven Architecture:** All design md docs completed in `/docs`.
- [ ] **Multistep Agent:** Active memory across all 4 phases.
- [ ] **MCP Apps:** Native Form and Mock Payment interface running inside chat.
- [ ] **A2UI Protocol:** Dynamic components streaming (no static raw HTML).
- [ ] **100+ Listings:** Mock database with 10 categories x 10 brands.
- [ ] **Outbound Integrations:** Twilio Voice, Twilio SMS, SendGrid, and Slack verified.
- [ ] **Observability:** OTel tracing visible in Langfuse / Arize Phoenix dashboard.
- [ ] **Containerization:** Clean multi-stage `Dockerfile` and `docker-compose.yml`.
