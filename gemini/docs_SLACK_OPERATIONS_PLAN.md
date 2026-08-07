# Slack Sales Operations & Dealer Alerts Plan

## 1. Strategic Purpose & Placement
Slack serves as the internal command center for dealership managers and sales representatives. It bridges autonomous AI customer discovery with real-time human sales intervention.

```
+-----------------------+     +-------------------+     +-----------------------+
| High-Intent Customer  | --> | Slack Webhook /   | --> | Dealer #sales-leads   |
| Action (Match/Checkout)|     | Bot Gateway       |     | Channel Alert         |
+-----------------------+     +-------------------+     +-----------------------+
```

---

## 2. Slack Notification & Interactive Bot Capabilities

### A. Real-Time High-Intent Lead Notification
* **Trigger:** Customer completes MCP Form App or ranks a vehicle with >90% match score.
* **Payload Format:** Rich Block Kit layout displaying user criteria, match details, sentiment analysis, and action buttons.

```json
{
  "blocks": [
    {
      "type": "header",
      "text": { "type": "plain_text", "text": "🔥 High-Intent Lead Matched!" }
    },
    {
      "type": "section",
      "fields": [
        { "type": "mrkdwn", "text": "*Customer:* Jane Doe
*Target Date:* Next Tuesday" },
        { "type": "mrkdwn", "text": "*Budget:* $65,000
*Matched:* 2024 BMW i4 eDrive40" }
      ]
    },
    {
      "type": "section",
      "text": { "type": "mrkdwn", "text": "*AI Reasoning:* High match due to daily 40-mile commute, EV charging desire, and active safety preference." }
    },
    {
      "type": "actions",
      "elements": [
        { "type": "button", "text": { "type": "plain_text", "text": "Claim Lead" }, "style": "primary", "value": "claim_lead_104" },
        { "type": "button", "text": { "type": "plain_text", "text": "Initiate Outbound Call" }, "value": "call_lead_104" }
      ]
    }
  ]
}
```

### B. Interactive Slash Command (`/match-status`)
Sales reps can query active customer sessions directly inside Slack:
* `/match-status <session_id>`: Returns active interview stage, selected vehicles, and sentiment indicators.
* `/override-match <session_id> <vehicle_id>`: Allows sales reps to push an alternative vehicle recommendation directly into the user's live web session.

---

## 3. Implementation Verification Checklist
- [ ] Slack App created with Incoming Webhooks & Bot Token scopes (`chat:write`, `commands`).
- [ ] Verified Block Kit rendering across desktop and mobile Slack clients.
- [ ] Tested interactive button callbacks targeting backend API endpoints.
