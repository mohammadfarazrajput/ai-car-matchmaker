# A2UI Protocol — the real wire format

**Tier: SHIP.** A2UI is an explicit, graded requirement: *"Render car catalogues and live agent
progress using Dynamic UI driven by A2UI — not static HTML."*

**Read this before writing any UI code.**

---

## 1. The correction

The `gemini/docs_SYSTEM_ARCHITECTURE.md` draft specifies this payload:

```json
{ "protocol": "A2UI/1.0", "action": "RENDER_COMPONENT", "component": { "type": "…", "props": {…} } }
```

**No part of that exists in A2UI.** There is no `protocol` field, no `action` field, and no
`RENDER_COMPONENT` message type. Building against it would mean shipping a bespoke JSON renderer
while claiming A2UI compliance — a claim a judge can falsify by opening the network tab.

## 2. What A2UI actually is

A stream of **newline-delimited JSON**. Every message carries `version` plus **exactly one** of
four keys:

| Key | Purpose |
|---|---|
| `createSurface` | Open a surface and bind it to a component catalog |
| `updateComponents` | Add or replace component definitions on a surface |
| `updateDataModel` | Write a value into the surface's data model at a JSON Pointer path |
| `deleteSurface` | Remove a surface |

The separation of **structure** (`updateComponents`) from **data** (`updateDataModel`) is the
core idea, and it is what enables progressive rendering: emit the skeleton immediately, stream
values in as they resolve.

### Real messages

```json
{"version":"v1.0","createSurface":{"surfaceId":"contact_form_1","catalogId":"https://a2ui.org/specification/v1_0/catalogs/basic/catalog.json"}}
```

```json
{"version":"v1.0","updateComponents":{"surfaceId":"contact_form_1","components":[
  {"id":"root","component":"Column","children":["name_field"]},
  {"id":"name_field","component":"TextField","label":"Name","value":{"path":"/contact/name"}}
]}}
```

```json
{"version":"v1.0","updateDataModel":{"surfaceId":"contact_form_1","path":"/contact/name","value":"John Doe"}}
```

Note the shape: components are a **flat list with `id`s**, and hierarchy is expressed by
`children` holding ID references — not by nesting. Data binding is `{"path": "/json/pointer"}`.

### Actions come back to the agent

```json
{"id":"submit_button","component":"Button","action":{"event":{"name":"submitContactForm","context":{"formId":"contact_form_1"}}}}
```

Clicking emits an action message back to the agent carrying `name` and `context`. This is how the
A2UI surface drives the state machine — the interview form, the "Select this car" button, and the
refine-search chips all route through it.

---

## 3. Version pinning

Three spec versions are live: **v0.9**, **v0.9.1**, **v1.0**. `@copilotkit/a2ui-renderer` tracks
its own release train and publishes canary tags aggressively.

**Pin `version` in every emitted message to exactly the version your renderer implements**, pin
the npm package to an exact version, and commit the lockfile. A silent renderer upgrade
mid-hackathon is a category of bug you cannot afford on day 2.

---

## 4. Our surfaces

Four surfaces cover the whole flow. Each maps to a phase of the state machine.

| Surface | When | Components | Why A2UI rather than static |
|---|---|---|---|
| `interview` | Phase 1 | Column · Text · chips for category · range for budget · date picker · Button | The agent adds and removes fields as slots fill — the form is genuinely agent-authored |
| `progress` | Phases 2–3 | Text · list rows streamed as search runs | This is the brief's "live agent progress · search status · reasoning steps" |
| `results` | Phase 3 | Card list, one per ranked car, with score breakdown and trade-off text | Card count and content are decided by the agent at runtime |
| `checkout_launcher` | Phase 4 | Button that opens the MCP form app | Bridges A2UI to MCP Apps |

### The progress surface is worth doing well

It is the requirement most entries will fake with a spinner. Streaming real reasoning steps —
*"searching 180 listings"* → *"31 match category and budget"* → *"ranking on 4 criteria"* →
*"top match: i4 eDrive40, 0.91"* — is cheap with `updateComponents` and demonstrates exactly what
the brief asks for. Emit one message per step from the agent's actual progress, not a scripted
animation.

### Results cards carry the reasoning

Each card binds to the ranking output from [01](01-CHANNEL-ARCHITECTURE.md):

```
/results/0/headline        2024 BMW i4 eDrive40
/results/0/score           0.91
/results/0/breakdown/*     budget .88 · category 1.0 · features .75 · date 1.0
/results/0/tradeoff        "285 mi range and 31-min 10–80% charging beat the EQE's
                            260 mi, but you give up 1.1s to 60 mph and ~$4k on
                            5-year depreciation."
```

Binding the breakdown into the card — rather than only into prose — is what makes "explains its
reasoning" inspectable rather than assertable.

---

## 5. Implementation notes

- **Transport.** A2UI messages ride the AG-UI SSE stream alongside text and tool events. They do
  not need a separate channel.
- **Catalog.** Start from the basic catalog at the URL above. Register a `CarCard` extension only
  if the basic components genuinely cannot express the card — every custom component is surface
  area that must render correctly under time pressure.
- **JSONL discipline.** One JSON object per line, no pretty-printing on the wire. Renderers parse
  line-by-line; a pretty-printed stream breaks progressive rendering.
- **Non-web channels ignore A2UI entirely.** The adapter for SMS or voice receives the
  channel-neutral `AgentMessage` and never sees a surface. Only web adapters subscribe to A2UI
  frames.

---

## References

- [A2UI v1.0 specification](https://a2ui.org/specification/v1.0-a2ui/)
- [A2UI v0.9.1 specification](https://a2ui.org/specification/v0.9.1-a2ui/)
- [Protocol source](https://github.com/a2ui-project/a2ui/blob/main/specification/v0_9/docs/a2ui_protocol.md)
- [CopilotKit A2UI notes](https://deepwiki.com/CopilotKit/generative-ui/4.1-a2ui-specification)
- [A2UI Composer](https://a2ui-composer.ag-ui.com/) — visual editor that emits real A2UI JSON, useful for checking our output by eye
