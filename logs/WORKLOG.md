# Work Log

Newest last. One entry per unit of work.

---

## 2026-08-08

**Read the existing docs.** 5 files in `docs/`, 1,783 lines. Specification only — no code, no git repo.

**Verified dependencies against PyPI/npm.** Found two pins that cannot install:
`ag-ui-langgraph>=0.1.0` (latest 0.0.42) and `copilotkit>=1.61.0` (PyPI is 0.1.94).
`deepgram-sdk` is at 7.6.0 while all code samples target the removed v3 API.

**Wrote `docs/PLAN.md`.** First plan revision. Flagged the missing MCP Apps host, the
listing schema's inability to match a target date, and the undefined ranking algorithm.

**Created the git repo.** `git init -b main` in `/mnt/data/bmw`. Needed
`git config --global --add safe.directory /mnt/data/bmw` — the mount is root-owned, uid is 1000.
Moved `docs/README.md` to repo root so its links resolve. Added `.gitignore` and `.env.example`.
→ commit `ec7f6f9`

**Added LICENSE, fixed placeholder URLs.** README claimed MIT with no LICENSE file.
Replaced `your-username` in both clone commands.
→ commit `80ef88f`

**GitHub setup.** Repo created by Faraz, empty and public — no auto-init commit, so the push was
clean. Added remote, pushed, set 11 topics. Description and MIT license detected.
→ https://github.com/mohammadfarazrajput/ai-car-matchmaker

**Verified free-tier reality** (searches, not memory). SendGrid free plan retired 2025-05-27.
Twilio A2P 10DLC needs a paid account, $44 + $15/campaign, 10–15 day review — trial accounts
cannot register at all. WhatsApp needs multi-day Meta Business Verification. Deepgram and Slack
are genuinely free.

**Verified the real A2UI wire format.** Gemini's drafts specify a fabricated payload
(`"protocol": "A2UI/1.0"`, `"action": "RENDER_COMPONENT"`). Real A2UI is JSONL carrying exactly
one of `createSurface` / `updateComponents` / `updateDataModel` / `deleteSurface`.

**Wrote `claudedocs/` — 9 documents, 1,283 lines.** Final plan. Core design: one
transport-agnostic match core with thin channel adapters, cross-channel session resume, shared
notification dispatcher. Scope tiered SHIP / STRETCH / DESIGNED.
→ commit `6505c7b`, pushed

**Feedback from Faraz:** work in smaller confirmable steps, ask before each; maintain log files.
Created `logs/WORKLOG.md` and `logs/DECISIONS.md`. Saved to memory.

**Installed spec-kit.** `specify init --here --integration claude --force --ignore-agent-tools`.
The `--ai` flag from the docs no longer exists; it is `--integration`. Agent detection also fails
because the `claude` binary isn't on PATH in this shell, hence `--ignore-agent-tools`.
Added `.specify/` and 10 `speckit-*` skills under `.claude/skills/`.

**Installed the `mcp-apps-builder` skill** (`npx skills add mcp-use/mcp-use`). Landed in
`.agents/skills/`, symlinked into `.claude/skills/`, plus `skills-lock.json`. Snyk rated it
Med Risk at install; Socket clean.

**Checked the skill against the MCP Apps spec — it does not align.** `references/views.md`
contains no `resourceUri`, `_meta`, `ui://`, `text/html;profile=mcp-app` or postMessage; it
documents mcp-use v2's own runtime bridge. Decision #2 (Python `FastMCP`) stands; skill is idle.
→ decision #20

**Ratified the constitution** — `.specify/memory/constitution.md` v1.0.0. Six principles:
Protocol Fidelity (non-negotiable), Zero-Key Demo, Honest Ranking (non-negotiable), Truthful
Artifacts, Reproducible Builds, Scope Discipline. Template shipped 5 principle slots; added a
sixth following the same pattern. No placeholders left, no extension hooks registered.
It supersedes `docs/`, `gemini/` and `claudedocs/` where they conflict.

**Wrote the baseline spec** — `specs/001-ai-car-matchmaker/spec.md`. 7 prioritised user stories,
31 functional requirements, 5 mandated constraints, 12 success criteria, 6 key entities.
Zero `[NEEDS CLARIFICATION]` markers: every gap had a defensible default, recorded in Assumptions
instead of deferred as a question. Quality checklist passed on the second iteration — see
`checklists/requirements.md` for the three issues corrected.

**Ran `/speckit-plan`** — `specs/001-ai-car-matchmaker/`: plan.md, research.md (10 findings),
data-model.md (7 entities), quickstart.md (10 validation scenarios), and 4 contracts
(mcp-apps, a2ui-surfaces, agent-api, channel-adapter). Constitution gate PASS both pre-Phase 0
and post-Phase 1; Complexity Tracking omitted as unused.

Design decision worth recording: the ranking scorer is handed a `ScorableListing` projection that
omits `make`, `model` and `provider.name`. Brand neutrality becomes structural rather than a matter
of discipline — the scorer cannot favour a manufacturer because it cannot see one. SC-006's masking
test then guards the projection against regression.

**Ran `/speckit-tasks`** — `specs/001-ai-car-matchmaker/tasks.md`, 95 tasks across 12 phases.
90 SHIP, 5 STRETCH; 4 DESIGNED items listed with no implementation task so they cannot drift into
being demonstrated. 20 parallelisable. Two hard checkpoints (D1, D2-MID) written in as gates that
cancel downstream STRETCH work rather than compressing it.

T058 ("read `examples/basic-host` first") deliberately precedes T059 (`McpAppHost`, 2h timebox),
and T061 is the pre-agreed cloudflared/Claude-connector fallback — so the fallback is a decision
already made rather than an improvisation under pressure.

**Agent B (opencode) — Phase 1 scaffold.** Created `frontend/` tree: T007 (package.json, all deps
exact-pinned — no caret/tilde), T009 (ESLint 10 flat config + Prettier 3.9.6), T025 (Next.js 16.3.0
+ CopilotKit provider). Dependencies: `@copilotkit/a2ui-renderer`, `react-core`, `react-ui` all at
1.66.2 (matching family); React 19.2.8; TypeScript 7.0.2. Versions verified against npm registry.
Lockfile pending — Node.js/npm not available in this env; must run `npm install` before first build.
Note from Agent A: canary tags exist on `@copilotkit/a2ui-renderer` — all pins must be exact 1.66.2.
→ commit `dbf1ba8`

**T005 / T006 / T013 (backend).** Package tree created; `requirements.txt` written with exact pins;
resolution verified by real install into a scratch venv (118 packages).

Principle V earned its keep. Of the versions I wrote from memory, **five were wrong** — `httpx
0.29.1` and `pytest 9.1.2` do not exist at all. A real resolve then found a genuine conflict:
`deepagents 0.7.5` requires `langchain-core>=1.5.0`, so the whole LangChain family moved to
`langchain 1.3.14` / `langchain-core 1.5.3` / `langgraph 1.2.10` / `langgraph-checkpoint 4.2.0`.

**Bigger finding: `mcp==2.0.0` has no `FastMCP`.** The official `qr-server` example we planned
against targets 1.x. 2.0.0 instead ships **first-class MCP Apps** as `mcp.server.apps.Apps`, an
`Extension` passed to `MCPServer(extensions=[apps])`, with `APP_MIME_TYPE ==
"text/html;profile=mcp-app"` and `_meta.ui.*` emitted by the SDK rather than hand-written.
Better than the plan — less to get wrong on a NON-NEGOTIABLE principle.

Also surfaced a requirement we did not have: SEP-2133 graceful degradation. `client_supports_apps(ctx)`
lets a UI-bound tool return usable text to hosts that never negotiated the Apps capability. Added to
the contract — it is what keeps the T061 fallback honest.

**The wire contract did not change**, so Agent B is unaffected and no cross-agent coordination was
needed.

**Agent B (opencode) — Phase 3: A2UI renderer + ChatPanel.** T031: built the A2UI v1.0 type
system (`types.ts`), surface state store (`store.ts`), and React renderer (`renderer.tsx`) covering
all basic catalog components — Text, Image, Icon, Row, Column, List, Card, Button, TextField,
ChoicePicker, Slider, DateTimeInput, Divider. T032: AG-UI SSE stream parser (`ag-ui-stream.ts`)
consuming `POST /agent` events, A2UIProvider context, and `ChatPanel.tsx` wiring the stream to
rendered surfaces. Replaced the CopilotKit sidebar with the direct AG-UI approach mandated by the
contracts. CopilotKit packages remain in package.json for potential future use. Layout and page
updated to use A2UIProvider + ChatPanel. Commit `8722fc3`.
→ commits `dbf1ba8`, `8722fc3`

**Agent B (opencode) — Phase 5-8: remaining frontend tasks.** T071: NotificationPanel.tsx displaying
rendered notification content (email HTML, Slack blocks, SMS text) with mock/live/failed status badges
per channel. T075: session resume route at `src/app/s/[code]/page.tsx` — follows redirect from
`GET /s/{code}`, or shows 410 with the error message and a "start fresh" button per FR-023. T079:
multi-stage Dockerfile with `NEXT_PUBLIC_*` as build args (not runtime env), standalone output mode,
node:22-alpine base. Commit `07b656f`.

All assigned tasks complete except T059 (McpAppHost), held for pairing with Agent A.
→ commits `dbf1ba8`, `8722fc3`, `07b656f`

**Contract stub live (T010, T022, T024 + the A2UI emitter from T029).**
`backend/app/{config,main,stub_data}.py` and `backend/app/a2ui/{emitter,surfaces}.py`.
Verified end to end: 61 A2UI frames over SSE, every one valid, single-line, and free of the
fabricated `protocol`/`RENDER_COMPONENT`/`props` shape. `/health` reports all channels `mock`,
which is the zero-key state working as designed.

**Port moved 8000 → 8010.** Port 8000 on this machine is already held by another service (an
Express app, not ours). Left it alone; changed our port instead and propagated through
`contracts/agent-api.md`, `.env.example`, `quickstart.md` and `tasks.md`.

The emitter validates on the way out rather than trusting callers — `to_jsonl` refuses a frame
carrying a `props` object or a top-level `protocol` key. Protocol fidelity is NON-NEGOTIABLE, so it
is enforced in code rather than in review.

Stub data deliberately ranks a Tesla above the BMW. A stub that rehearsed a BMW-first result would
set the wrong expectation for a ranker that is required to be brand-neutral.

**Agent B — renderer compatibility fix.** Backend stub uses `Select`, `DateField`, and a richer
`Card` pattern (title/subtitle/imageUrl/body props) than the basic catalog spec. Updated
`types.ts` with `SelectComponent` and `DateFieldComponent`, updated `CardComponent` to accept both
`child` ref and direct content props, updated `ButtonComponent` with `label` prop, and updated
`List` renderer to handle `items` path (array of objects). Updated `next.config.ts` API port default
to 8010. Removed dead `CopilotKitProvider.tsx`, wired `NotificationPanel` into `ChatPanel` via
`STATE_SNAPSHOT` notifications. Verified backend SSE stream: 61 valid A2UI frames, interview +
progress + results surfaces all render correctly. Commits `f13bd1d`, `abd5ce8`.

**T014–T019 (backend).** Pydantic entities, curated brand matrix, generator, dataset, coverage test.

`schemas.py` makes the functional requirements executable rather than documentary — a listing that
could not satisfy FR-008 now fails construction: EV spec present iff electrified, new cars at zero
miles, availability windows ordered and non-overlapping. `ScorableListing` omits `make`, `model` and
`provider.name` by construction, so Principle III is structural.

`brand_matrix.json` is authored, not sampled. 12 categories x >=10 plausible manufacturers, with a
model list per pair — random pairing from a flat brand pool yields a Lamborghini minivan.

Generated **180 listings, 12 categories, >=10 makes each**, all validating. Pass 1 emits every
(category, make) pair so FR-007 holds by construction; pass 2 tops up for volume.

**Mutation-tested the coverage gate**: thinning `truck` to 3 makes correctly failed 3 of 12
assertions. A gate that cannot fail is not a gate.

Pydantic v2 rejects non-annotated class attributes — `WEIGHTS` and `CORE_SLOTS` needed `ClassVar`.

**Answered Agent B; dropped SMS; wired real LLM keys.**

*Action dispatch (contract gap Agent B found).* `contracts/agent-api.md` never said how A2UI actions
return to the agent. Now defined: `POST /agent` with `{session_id, action:{name, context}}` — the
same endpoint, because actions are conversational turns and `setBudget` must be able to trigger a
re-rank and stream frames back. Implemented in the stub; verified that filling the fourth slot
auto-runs research → progress → results (56 frames), and that an unknown action returns `RUN_ERROR`
rather than failing quietly.

*SMS dropped* per Faraz — decision #25. Removed from requirements, config, schemas, contracts,
tasks (T001, T094 deleted), `.env.example` and `/health`.

*LLM keys.* Both provided keys work. Two findings: **`gemini-2.5-flash` is 404 "no longer available
to new users"** — the model named across every planning document — and `gemini-2.0-flash` 429s
immediately, confirming the free-tier limits Faraz raised. Pinned `gemini-3.5-flash`, dev default
`groq`.

*Frontend lockfile blocked.* `npm install` fails: `typescript-eslint@8.66.0` peers
`typescript >=4.8.4 <6.1.0`, but Agent B pinned `typescript@7.0.2`. No published typescript-eslint
supports TS 7. Highest compatible TypeScript is **6.0.3**. Left the fix to Agent B — `frontend/` is
theirs.

**Agent B — fixes from Agent A's answers.** (1) TypeScript `7.0.2` → `6.0.3` to satisfy
`typescript-eslint@8.66.0` peer dep. (2) Wired action dispatch: `ChatPanel.dispatchAction` sends
`POST /agent` with `{ session_id, action: { name, context } }` — name/context verbatim from
`action.event`, no interpretation. Actions now flow through the same SSE stream. (3) No SMS cleanup
needed — `NotificationPanel` is channel-agnostic. Commit `108eaad`. Agent A to re-run `npm install`
and commit the lockfile.

**T020 — LLM providers.** Four: `google`, `vertex`, `groq`, `echo`. 29 tests green.

Vertex added per Faraz's rate-limit challenge; `langchain-google-vertexai==3.2.4` verified to
resolve against the existing set before being written in. It is never the committed default —
an evaluator can paste an API key but cannot be asked to onboard to GCP (Principle II).

**Cross-provider bug found by testing rather than reading**: `langchain-google-genai` 4.x returns
`AIMessage.content` as a **list of content blocks**, while Groq returns a plain `str`. Any code
calling `.strip()` or `json.loads()` on `.content` works with one provider and breaks with the
other — and it would have surfaced only when switching to Google for the recorded demo. Added
`message_text()`; every consumer of a model response must go through it.

Providers refuse loudly on a missing credential rather than silently degrading to `echo` — a demo
that quietly stops using the real model is worse than one that refuses to start.

The `echo` model does real regex slot extraction, so CI exercises the interview path without
credentials. Its own test caught a gap: `\blease\b` did not match "leasing".
