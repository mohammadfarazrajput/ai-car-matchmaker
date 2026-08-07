# Voice & Calling

**Browser voice: STRETCH. Phone: DESIGNED.**
Split deliberately — they share a pipeline but have completely different cost profiles.

---

## 1. Why the split

Gemini's draft treats voice as one capability. It is two, and only one is affordable.

| | Browser voice | Phone |
|---|---|---|
| Audio path | WebAudio → WebSocket → Deepgram | PSTN → Twilio → Media Stream → Deepgram |
| Extra infrastructure | none | Twilio number, public webhook, TwiML, tunnel |
| Account gate | Deepgram signup, instant | Toll-free verification, days |
| Build estimate | ~3h | ~6h |
| Demo value | **High** — visible, immediate | Moderate — hard to show on video |

Browser voice gets you the entire "conversational car buying" story for half the effort and none
of the telephony risk. Phone is specified here so the deck can show the architecture, and so it is
a genuine day-3 continuation rather than a hand-wave.

**Deepgram already hosts Whisper.** Gemini's "Deepgram STT + Whisper" is one pipeline with a model
parameter, not two systems. Use `nova-3` for streaming; Whisper is a fallback model choice for
noisy prerecorded audio, not a separate integration.

---

## 2. Browser voice — STRETCH

The interview, hands-free, in the same web surface that already renders A2UI.

```
 mic button ──► MediaRecorder ──► WS /api/voice/stream ──► Deepgram nova-3
                                                                │ interim + final
                     A2UI interview surface ◄── match core ◄────┘
                                │
                     Deepgram aura TTS ──► audio playback
```

### Design decisions

**Voice augments the surface, it does not replace it.** While the customer speaks, the A2UI
interview surface fills in live — budget slider moves, category chip highlights. That
simultaneity is the demo moment: they said it, and the UI *understood* it. A voice-only mode
would throw away the thing being graded.

**Interim transcripts drive nothing.** Render them as ghost text for feedback; only commit slot
extraction on `is_final`. Acting on interim results produces visible flapping.

**Barge-in.** Stop TTS playback the instant the mic detects speech. Without it the demo feels
like an IVR.

**Push-to-talk over VAD.** Open-mic voice activity detection is fragile in a noisy room, which is
exactly where the demo happens. Hold-to-talk is boring and works.

### Configuration

```
DEEPGRAM_API_KEY=          # $200 credits, no card — see 07
DEEPGRAM_STT_MODEL=nova-3
DEEPGRAM_TTS_MODEL=aura-asteria-en
```

Absent key → the mic button is disabled with a tooltip, text input unaffected. Per the zero-key rule.

### Checkpoint

Start browser voice **only if the SHIP tier is green by the Day 2 midpoint**. It is the most
likely thing to eat the deck-and-video budget, and a missing deck costs more marks than missing
voice.

---

## 3. Phone — DESIGNED

Specified, not built. Present as architecture.

### 3a. Inbound concierge

```
Customer dials ──► Twilio Voice ──► TwiML <Connect><Stream>
                                          │  bidirectional media over WS
                                          ▼
                          /api/voice/inbound  ──► Deepgram nova-3
                                          │
                          match core (same interview state machine)
                                          │
                          Deepgram aura ──► μ-law 8kHz ──► Twilio ──► caller
```

The core is unchanged — this is precisely what the adapter model buys. `PhoneAdapter` implements
`deliver`/`receive` and the interview logic is untouched.

**Scope on the phone is deliberately narrow.** Capture only the four core slots: intent, budget,
category, target date. Feature preferences and trade-off comparisons need to be *seen*. Per
[01](01-CHANNEL-ARCHITECTURE.md) Rule 2, once the slots are filled the call ends with a handoff:

> *"I've found four matches. I'm texting you a link to see them — anything else before I let you go?"*

That SMS carries the resume token. The customer lands in web with the interview pre-filled. That
handoff *is* the feature.

### 3b. Outbound follow-up

Trigger: booking confirmed on a high-value vehicle. Queue a call at +15 minutes to confirm the
test drive slot, with warm transfer to a human if requested.

**Honesty note for the deck:** unsolicited outbound calling is regulated (TCPA in the US, similar
regimes elsewhere) and requires prior express consent. In a real deployment this needs an opt-in
checkbox at checkout and a suppression list. Say so in the deck — automotive judges know this, and
naming it reads as competence rather than naivety. The mock booking form includes the consent
checkbox even though nothing dials.

### Blockers, quantified

| Blocker | Detail |
|---|---|
| Toll-free verification | Free, but takes days. Start it now if phone is ever wanted |
| A2P 10DLC | Irrelevant for voice, blocks the SMS handoff — see [04](04-SMS.md) |
| Trial watermark | Trial calls play a "trial account" preamble |
| Public webhook | Media Streams need a reachable HTTPS endpoint; `cloudflared` for dev |
| Latency | The sub-300ms figure in the Gemini draft is optimistic once TTS and LLM are in the loop. Budget ~800ms round trip and design for it with filler phrases |

---

## 4. Verification checklist

**Browser voice (STRETCH)**
- [ ] Deepgram key resolves; WS connects and streams interim + final
- [ ] Slot extraction commits only on final transcripts
- [ ] A2UI interview surface updates live during speech
- [ ] Barge-in stops TTS within ~200ms
- [ ] Absent key → mic disabled, text path unaffected

**Phone (DESIGNED — for the deck)**
- [ ] Architecture diagram matches the adapter contract in [01](01-CHANNEL-ARCHITECTURE.md)
- [ ] Consent and TCPA constraint stated explicitly
- [ ] Handoff-to-web narrative shown as the terminal step
