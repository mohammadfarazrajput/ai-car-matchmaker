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

**Both agents share ONE working tree at `/mnt/data/bmw`.** There are no separate clones and no
separate branches — a working tree has exactly one HEAD, so two branches is not physically possible
here. Everything below follows from that.

### Forbidden — these mutate shared state and will destroy the other agent's in-flight work

```
git checkout <branch>    git switch    git rebase    git stash
git reset --hard         git clean     git merge     git pull
```

If you think you need one of these, **stop and say so.** Do not run it.

### Committing — always with an explicit pathspec

```bash
# Agent A                                 # Agent B
git commit -m "msg" -- backend/           git commit -m "msg" -- frontend/
```

The trailing `-- <dir>` is **not optional**. A bare `git commit` commits whatever happens to be
staged — including the other agent's files if they staged a moment earlier. The pathspec form
ignores the index and commits only those paths, which makes concurrent commits safe.

**New (untracked) files must be `git add`ed first** — a pathspec commit only sees files git already
tracks, and fails with `did not match any file(s) known to git` otherwise. So for anything new:

```bash
git add frontend/                          # scoped to YOUR directory only
git commit -m "msg" -- frontend/
```

`git add <your-dir>` is safe. `git add -A` and `git add .` from the repo root are not — they sweep
the other agent's files into your index.

### Other rules

- **Commit small and often.** Long-lived uncommitted work is what gets lost.
- Both agents commit to the **same branch** (`main`). This is safe *only* because the directory
  ownership in §1 is absolute.
- `git status` will show the other agent's files as modified. **That is normal.** Leave them alone.
- Pushing is Agent A's job, on Faraz's approval, and only when both agents are at rest.

> If you would rather have real branches, the correct tool is
> `git worktree add ../bmw-frontend -b feat/frontend`, which gives Agent B its own directory and
> HEAD. That requires repointing opencode at the new path — worth it for a longer project, probably
> not for a two-day one.

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
| End of Phase 3 (US1) | Both commit, run the interview end to end |
| **CHECKPOINT D1** | Interview + ranking working in the browser |
| Before T059 (`McpAppHost`) | **Pair on this** — see §6 |
| **CHECKPOINT D2-MID** | Both MCP Apps rendering in-chat |
| Before T081 | Verify the zero-key run from a clean clone |

There is no merging — one working tree, one branch. A sync point simply means both agents stop, commit
their own directory, and run the full test suite together before continuing.

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
> shared file listed in §1. We share one working tree, so stage and commit scoped to your directory
> only — `git add frontend/` then `git commit -m "msg" -- frontend/`. Both parts are mandatory.
> Never run `git add -A`, `git add .`, `git checkout`, `git rebase`, `git stash` or `git pull`.
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
