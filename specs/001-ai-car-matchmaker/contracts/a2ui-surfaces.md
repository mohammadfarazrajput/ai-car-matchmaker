# Contract: A2UI Surfaces

**Governs**: MC-002, FR-019, FR-020 · Constitution Principle I (NON-NEGOTIABLE)

Protocol version: **A2UI v1.0**. Emitted `version` must match the renderer's implemented version
exactly; both are pinned.

---

## Wire format

Newline-delimited JSON. One object per line, no pretty-printing — renderers parse line-by-line and
pretty-printing breaks progressive rendering.

Every message carries `version` plus **exactly one** of:

| Key | Purpose |
|---|---|
| `createSurface` | Open a surface, bind a component catalog |
| `updateComponents` | Add or replace component definitions |
| `updateDataModel` | Write a value at a JSON Pointer path |
| `deleteSurface` | Remove a surface |

Components are a **flat list with `id`s**; hierarchy comes from `children` holding ID references, not
nesting. Data binds via `{"path": "/json/pointer"}`. Interactions declare
`action.event.name` with a `context` object, and the host returns an action message to the agent.

> **Prohibited**: `{"protocol": "A2UI/1.0", "action": "RENDER_COMPONENT", …}`. No such fields exist in
> any published version. See research R2.

A2UI frames travel on the AG-UI SSE stream alongside text and tool events — no separate channel.

---

## Surfaces

### 1 · `interview` — Phase INTERVIEWING

Agent-authored: fields are added and removed as slots fill, which is what makes this dynamic UI
rather than a static form (FR-020, FR-005).

```
Data paths
  /interview/intent          "buy" | "rent" | null
  /interview/category        string | null
  /interview/budget/max      number | null
  /interview/target_date     ISO date | null
  /interview/missing         string[]      ← drives FR-005
```

Actions: `setIntent`, `setCategory`, `setBudget`, `setTargetDate`, `proceedAnyway`
(`proceedAnyway` carries the stated assumption required by FR-006).

### 2 · `progress` — Phases RESEARCHING → RANKED

The requirement most entries will fake with a spinner. **Every step must carry real figures from the
work actually performed** (FR-019) — one `updateComponents` per completed stage, driven by the
agent's progress, never a scripted animation.

```
/progress/steps[]   { label, detail, at }
```

Representative sequence — note the counts are real:

```
searching 180 listings
31 match category and budget
12 available on 3 September
ranking on 4 criteria
top match: i4 eDrive40 — 0.91
```

When nothing matches, the final step names the eliminating constraint and the offered relaxation
(FR-012).

### 3 · `results` — Phase RANKED

One card per ranked listing. Card count and content are decided at runtime.

```
/results/{i}/headline           "2024 BMW i4 eDrive40"
/results/{i}/score              0.91
/results/{i}/breakdown/budget   0.88
/results/{i}/breakdown/category 1.0
/results/{i}/breakdown/features 0.75
/results/{i}/breakdown/date     1.0
/results/{i}/reasoning          string   ← ≥1 supporting figure, ≥1 trade-off
/results/{i}/price_label        string
/results/{i}/image_url          string
```

Actions: `selectCar` (→ `checkout_launcher`), `explainMore`, `refineSearch`.

Binding `breakdown` into the card — not only into prose — is what makes FR-011 inspectable rather
than asserted.

### 4 · `checkout_launcher` — Phase CAR_SELECTED

A single Button whose action opens the booking MCP App. This is the bridge from A2UI to
[mcp-apps.md](./mcp-apps.md); it deliberately holds no booking logic of its own.

---

## Catalog

Start from the basic catalog:
`https://a2ui.org/specification/v1_0/catalogs/basic/catalog.json`

Register a custom `CarCard` **only** if basic components cannot express the results card. Every
custom component is surface area that has to render correctly under time pressure.

**The catalog defines exactly 18 components**: `AudioPlayer`, `Button`, `Card`, `CheckBox`,
`ChoicePicker`, `Column`, `DateTimeInput`, `Divider`, `Icon`, `Image`, `List`, `Modal`, `Row`,
`Slider`, `Tabs`, `Text`, `TextField`, `Video`. Emitting anything else while declaring this
`catalogId` is a protocol violation — the renderer has no definition to render against.
`emitter.CATALOG_COMPONENTS` enforces this at emission time.

Two traps worth naming: a single-choice dropdown is `ChoicePicker` with
`variant: "mutuallyExclusive"` and `options: [{label, value}]` — there is no `Select`. A date input
is `DateTimeInput` with `enableDate: true` — there is no `DateField`. And `Slider.steps` is the
**number of divisions**, not the increment.

---

## Non-web channels

Adapters for email, SMS and Slack receive the channel-neutral `AgentMessage` and never see a surface.
Only web adapters subscribe to A2UI frames. See [channel-adapter.md](./channel-adapter.md).

---

## Contract tests

- [ ] Every emitted line is valid JSON with exactly one of the four keys, plus `version`
- [ ] Emitted `version` equals the renderer's pinned version
- [ ] No frame contains `protocol`, `action: "RENDER_COMPONENT"`, or a `props` object
- [ ] Components are flat; hierarchy uses `children` ID references only
- [ ] `progress` step counts equal the real search figures for the same run
- [ ] `/results/{i}/breakdown/*` equals the `RankedResult.breakdown` for that listing
- [ ] Stream is newline-delimited with no pretty-printing
- [ ] Every emitted component name is one of the catalog's 18
