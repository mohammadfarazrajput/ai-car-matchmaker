# Parallel Work Split — Claude Code ⇄ opencode

Two agents, one repo. **Both agents read this file before touching anything.**

---

## 1. The seam

The split follows the **language and directory boundary**, not the task-list order — that is the only
line in this project with near-zero conflict surface.

| | **Agent A — Claude Code** | **Agent B — opencode** |
|---|---|---|
| Owns | `backend/**` | `frontend/**` |
| Language | Python | TypeScript |
| Branch | `feat/backend` | `feat/frontend` |
| Tasks | T005–T006, T008, T010, T012–T024, T026–T030, T033–T046, T047–T057, T060–T070, T072–T074, T076–T078 | T007, T009, T025, T031–T032, T059, T071, T075, T079 |

**Neither agent edits the other's directory. Ever.** If you need something across the boundary, the
contract already specifies it — build to the contract, do not reach across.

### Shared files — single owner each

| File | Owner | Rule |
|---|---|---|
| `docker-compose.yml` | A | B requests changes, does not edit |
| `.env.example` | A | Must match `backend/app/config.py` |
| `README.md` | A | Written at T082 |
| `specs/**`, `claudedocs/**`, `.specify/**` | A | **Frozen.** See §3 |
| `logs/WORKLOG.md` | Both | Append only, never rewrite |
| `logs/DECISIONS.md` | A | B proposes, A records |

---

## 2. Git protocol

```bash
# Both, once
git checkout main && git pull
git checkout -b feat/backend      # or feat/frontend

# Before every commit
git fetch origin && git rebase origin/main

# Merge to main at checkpoints only — never mid-phase
```

- **Commit small and often.** A 20-file commit is unmergeable in parallel work.
- **Never push to `main` directly.** Merge via the checkpoint sync in §5.
- **Never `git add -A` from the repo root** — it will sweep the other agent's files. Stage your own
  directory explicitly: `git add backend/` or `git add frontend/`.
- A rebase conflict outside your directory means the split was violated. Stop and reconcile rather
  than resolving it.

---

## 3. The contracts are frozen

`specs/001-ai-car-matchmaker/contracts/` is the interface between the two halves. It was written
before any code so it could serve exactly this purpose.

**Neither agent changes a contract unilaterally.** If reality forces a change: stop, state the
problem, get agreement, amend the contract, then both sides update. A contract silently edited by one
agent is the single most likely way this parallelisation fails.

| Contract | Binds |
|---|---|
| `agent-api.md` | A implements, B consumes |
| `a2ui-surfaces.md` | A emits frames, B renders them |
| `mcp-apps.md` | A serves `ui://` resources, B hosts them |
| `channel-adapter.md` | A only |

Also frozen and binding on both: `.specify/memory/constitution.md`. Principles **I (Protocol
Fidelity)** and **III (Honest Ranking)** are NON-NEGOTIABLE — they may be strengthened, never
weakened.

---

## 4. Unblocking B — A goes first, briefly

B cannot render anything against a backend that does not exist. So A's first job is not the agent,
it is the **contract stub**:

**A, within the first ~45 minutes (T022, T024, then a stub):**
- `GET /health` returning the real shape from `contracts/agent-api.md`
- `POST /agent` streaming SSE that emits **real A2UI frames** for the `interview` surface, canned but
  protocol-correct
- `GET /api/listings` returning ~5 hardcoded projections with a plausible `score_breakdown`

Announce the moment it is up. B then has something real to build against and both halves proceed
independently. Replacing canned data with the real agent is invisible to B, because the wire format
does not change.

---

## 5. Sync points

| When | What |
|---|---|
| After A's stub is live | B starts frontend work in earnest |
| End of Phase 3 (US1) | Both merge to `main`, run the interview end to end |
| **CHECKPOINT D1** | Full merge. Interview + ranking working in the browser |
| Before T059 (`McpAppHost`) | **Pair on this** — see §6 |
| **CHECKPOINT D2-MID** | Full merge. Both MCP Apps rendering in-chat |
| Before T081 | Merge everything, verify the zero-key run from a clean clone |

At each sync: both rebase on `main`, merge, run the full test suite, fix together.

---

## 6. T059 — `McpAppHost` is the exception

It sits in `frontend/`, so it is nominally B's. **It should not be done alone by either agent.**

It is the highest-risk item in the project: the host-side API of
`@modelcontextprotocol/ext-apps/app-bridge` is undocumented, it carries a hard 2-hour timebox, and
the fallback (T061 — cloudflared + Claude custom connector) is a judgement call that ends the
attempt. Whoever runs the clock must be willing to stop.

**Before starting**: T058 — read `examples/basic-host` in `modelcontextprotocol/ext-apps`. Both
agents. It is the only working reference.

---

## 7. Rules that are not negotiable

1. **Exact version pins, no caret ranges, lockfiles committed** (Principle V). B: no `^` in
   `package.json`. A: no `>=` in `requirements.txt`.
2. **Every task carries its tier.** STRETCH work does not begin until CHECKPOINT D2-MID is green —
   this applies to both agents independently.
3. **Zero-key demo** (Principle II). Nothing either agent builds may require a credential the
   evaluator lacks, beyond the LLM.
4. **A2UI must be the real wire format.** No `protocol` field, no `RENDER_COMPONENT`, no `props`
   object. B: if a frame will not render, the fix is in A's emitter, not a translation shim in the
   renderer.
5. **Append to `logs/WORKLOG.md` when a phase completes**, so the other agent can see where you are.

---

## 8. Brief for opencode

Paste this to start Agent B:

> You are Agent B in a two-agent build of the AI Car Matchmaker (Amulate Summer Hackathon 2026, hosted
> by BMW). Repo: `/mnt/data/bmw`.
>
> **Read first, in order**: `logs/WORK-SPLIT.md` (this file — the rules),
> `.specify/memory/constitution.md` (binding principles),
> `specs/001-ai-car-matchmaker/spec.md`, `specs/001-ai-car-matchmaker/tasks.md`, and every file in
> `specs/001-ai-car-matchmaker/contracts/`.
>
> **You own `frontend/` only.** Never edit `backend/`, `specs/`, `claudedocs/`, `.specify/` or any
> shared file listed in §1. Work on branch `feat/frontend`. Stage with `git add frontend/`, never
> `git add -A`.
>
> **Your tasks**: T007, T009, T025, T031, T032, T071, T075, T079. Hold T059 until we pair on it.
>
> **Non-negotiable**: exact version pins with no caret ranges and a committed lockfile; A2UI frames
> render as received — if one will not render, report it rather than adding a translation shim; no
> feature may require a credential beyond the LLM.
>
> Agent A is building the backend and will announce when the contract stub is live at
> `localhost:8000`. Until then, build against the shapes in `contracts/agent-api.md` and
> `contracts/a2ui-surfaces.md`.
>
> Start with T007 and T025. Append to `logs/WORKLOG.md` as you complete each phase.
