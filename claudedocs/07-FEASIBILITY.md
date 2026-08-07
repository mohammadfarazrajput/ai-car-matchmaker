# Feasibility, Costs & Account Lead Times

Verified 2026-08-08. Every claim here was checked against current vendor documentation, not
recalled — several of these changed within the last 18 months and the older figures are still
widely repeated online, including in `docs/` and `gemini/`.

---

## 1. Verdict table

| Service | Free tier | Card required | Lead time | Verdict |
|---|---|---|---|---|
| **Slack** | Unlimited for our use | No | **Instant** | ✅ SHIP |
| **Resend** (email) | 3,000/month | No | **Instant** — `onboarding@resend.dev` | ✅ SHIP |
| **Deepgram** | $200 credits (~25,000 min STT) | **No** | Instant | ✅ STRETCH |
| **Google AI Studio** | Free tier | No | Instant | ✅ SHIP — the only hard dependency |
| **Arize Phoenix** | Open source, self-host | No | Instant | ✅ STRETCH |
| **Twilio SMS** | Trial credit, 5 verified numbers | No | **Days** (toll-free verification) | ⚠️ STRETCH |
| **Twilio Voice** | Trial credit, verified numbers only | No | **Days** | ⚠️ DESIGNED |
| **SendGrid** | ❌ **None since 27 May 2025** | Yes after trial | — | ❌ REPLACED by Resend |
| **WhatsApp** | 1,000 conv/mo, but gated | No | **Multi-day verification** | ❌ DROPPED |

---

## 2. Where money or time genuinely blocks you

### SendGrid — pay, and an alternative exists

Twilio retired the perpetual 100/day free plan on **27 May 2025**. New accounts: 60-day trial,
then **$19.95/month** minimum. `docs/IMPLEMENTATION.md` §2.7 and the Gemini email plan both
assume the retired tier.

→ **Switch to Resend.** 3,000/month free, and the sandbox sender works with no DNS wait. See
[05](05-EMAIL.md).

### Twilio A2P 10DLC — pay *and* wait, and the wait is fatal

To send SMS to arbitrary US numbers you need A2P 10DLC registration:

- Requires a **paid** account — trial accounts cannot register at all
- **$44** one-time brand + **$15** per campaign vetting + **$1.50–10** per campaign per month
- Campaign review takes **10–15 days**

No budget fixes a 10-day review inside a 2-day hackathon.

→ **Free path:** toll-free verification costs nothing and permits messaging to **5
pre-designated numbers** from a trial account. Sufficient for a demo. **Submit it today** — it is
the longest-lead free item in the project.

### WhatsApp — free, but gated behind multi-day verification

The Cloud API gives 1,000 free service conversations per month, but Meta Business Verification
requires business documents and takes several days. Unofficial sandboxes (Whapi.Cloud, Green API)
sidestep it, but then you are not using the Meta Business API your docs claim, and you have added
a third-party vendor for a channel the brief never asked for.

→ **Dropped.** Documented in the deck as a designed extension.

---

## 3. Start these now, in parallel with the build

Ordered by lead time. The first two cost nothing and unblock later work.

| When | Action | Blocks |
|---|---|---|
| **Immediately** | Twilio toll-free verification | All of [04](04-SMS.md) |
| **Immediately** | Slack app + bot token | [06](06-SLACK.md) — 5 minutes, do it first for a fast win |
| Today | Resend signup | [05](05-EMAIL.md) |
| Today | Google AI Studio key | Everything — this is the hard dependency |
| Before voice | Deepgram signup | [03](03-VOICE-CALLING.md) |

**Never paste keys into chat.** Put them in `.env`, which `.gitignore` already excludes. Verify
before every commit:

```bash
git check-ignore -v .env && git ls-files --error-unmatch .env 2>/dev/null && echo "LEAKED" || echo "safe"
```

---

## 4. Dependency versions — verified on the registries

`docs/IMPLEMENTATION.md` §2.2 contains two pins that **cannot install**.

| Doc pin | Actual latest | Action |
|---|---|---|
| `ag-ui-langgraph>=0.1.0` | **0.0.42** | ❌ unsatisfiable → `>=0.0.42,<0.1` |
| `copilotkit>=1.61.0` | **0.1.94** on PyPI (1.66.4 is the *npm* package) | ❌ unsatisfiable → `>=0.1.94` |
| `deepgram-sdk>=3.0.0` | **7.6.0** | installs, but §2.9/§2.10 call removed v3 methods |
| `langchain-google-genai>=2.0.0` | **4.3.2** | two majors ahead — re-verify kwargs |
| `deepagents>=0.7.0` | 0.7.5 | ✅ |
| `mcp` | **2.0.0** | ✅ missing from the docs — required for the MCP App servers |
| `@modelcontextprotocol/ext-apps` | 1.7.5 (npm only) | ✅ host side |
| `@copilotkit/a2ui-renderer` | 1.66.4 | ✅ pin exact, no `^` |
| `arize-phoenix` / `-otel` | 19.19.0 / 0.16.1 | ✅ |
| `openinference-instrumentation-langchain` | 0.1.70 | ✅ |
| `langfuse` | 4.14.3 | ✅ alternative to Phoenix |

### Also: Vertex AI vs Gemini API are different products

README and SPEC say "Vertex AI", `config.py` takes an API key, and the graph imports
`langchain-google-genai`. Vertex uses service-account ADC and `langchain-google-vertexai`; the
API-key path is Google AI Studio.

→ **Google AI Studio.** Far less setup, and the free tier is adequate. Delete every "Vertex AI"
mention.

---

## 5. Corrections carried from the Gemini drafts

| Claim | Reality |
|---|---|
| `{"protocol":"A2UI/1.0","action":"RENDER_COMPONENT"}` | Fabricated. Real A2UI is JSONL with `createSurface` / `updateComponents` / `updateDataModel` / `deleteSurface`. See [02](02-A2UI-PROTOCOL.md) |
| "Deepgram STT + Whisper" as two systems | One pipeline; Deepgram hosts Whisper as a model option |
| "SQLite / JSON Dataset" | Pick one. JSON loaded to memory — the brief puts persistence out of scope |
| Listing schema with `is_available BOOLEAN` | Cannot satisfy the required target-date matching. Needs availability *windows* |
| "Claude Agent SDK / LangChain / OpenAI SDK" | Pick one. DeepAgents |
| Sub-300ms voice round trip | Optimistic with LLM and TTS in the loop. Budget ~800ms |
| WeasyPrint PDF dossier | Drags in Pango/Cairo/GDK-Pixbuf, complicates Docker, nobody grades it |
| `/override-match` live session push | Needs a bidirectional session bus nothing else requires |
| SendGrid dynamic templates | Not in version control, cannot be tested offline, breaks the zero-key demo |

---

## 6. Honest capacity assessment

Two days is roughly 16–20 working hours.

| Block | Estimate |
|---|---|
| Required core — data, agent, A2UI, MCP Apps, Docker, README | **~12h** |
| BMW depth — trim data, trade-off explanations, premium checkout breakdown | ~4h |
| Deck + video | ~1.5h |
| Notification fan-out — Slack + email + SMS on one dispatcher | ~2.5h |
| Browser voice | ~3h |
| Observability + evals | ~2h |
| **Total** | **~25h** |

That is over budget against 16–20h, which is why [08](08-BUILD-ORDER.md) is ordered so the
overflow lands on STRETCH items and never on a graded requirement. The fan-out is included in SHIP
precisely because three channels on one dispatcher cost 2.5h, whereas three separate integrations
would cost 6h and have to be cut.

**Sources:** [SendGrid changelog](https://www.twilio.com/en-us/changelog/sendgrid-free-plan) · [SendGrid free plan discontinued](https://helpdesk.reusser.com/hc/en-us/articles/38602119422349-SendGrid-Free-Plan-Discontinued) · [A2P 10DLC quickstart](https://www.twilio.com/docs/messaging/compliance/a2p-10dlc/quickstart) · [A2P fees](https://help.gohighlevel.com/support/solutions/articles/155000005200-a2p-10dlc-messaging-fees-registration-monthly-and-carrier-costs) · [Twilio trial guide](https://www.twilio.com/docs/usage/tutorials/how-to-use-your-free-trial-account) · [Deepgram pricing](https://deepgram.com/pricing) · [WhatsApp API comparison](https://dev.to/kevin_menesesgonzlez/7-best-whatsapp-apis-for-developers-in-2026-compared-f6)
