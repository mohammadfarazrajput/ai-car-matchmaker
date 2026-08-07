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
