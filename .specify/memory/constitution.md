<!--
SYNC IMPACT REPORT
==================
Version change: (unversioned template) → 1.0.0
Bump rationale: MAJOR — initial ratification. All placeholder tokens replaced with
concrete governance for the AI Car Matchmaker project.

Modified principles:
  [PRINCIPLE_1_NAME] → I. Protocol Fidelity (NON-NEGOTIABLE)
  [PRINCIPLE_2_NAME] → II. Zero-Key Demo
  [PRINCIPLE_3_NAME] → III. Honest Ranking (NON-NEGOTIABLE)
  [PRINCIPLE_4_NAME] → IV. Truthful Artifacts
  [PRINCIPLE_5_NAME] → V. Reproducible Builds
  (added)           → VI. Scope Discipline

Added sections:
  Technology & Protocol Constraints (was [SECTION_2_NAME])
  Development Workflow & Quality Gates (was [SECTION_3_NAME])

Removed sections: none

Deferred TODOs: none
-->

# AI Car Matchmaker Constitution

Amulate Summer Hackathon 2026, hosted by BMW. Two-day build.
This constitution governs every specification, plan, and task in this repository.

## Core Principles

### I. Protocol Fidelity (NON-NEGOTIABLE)

The project is graded on protocol compliance, and compliance is externally verifiable.
Therefore:

- A2UI output MUST be the real wire format: newline-delimited JSON in which every message
  carries `version` plus exactly one of `createSurface`, `updateComponents`,
  `updateDataModel`, or `deleteSurface`. Bespoke envelopes such as
  `{"protocol": "A2UI/1.0", "action": "RENDER_COMPONENT"}` are prohibited.
- MCP Apps MUST use the official contract: `ui://` resource URIs, the
  `text/html;profile=mcp-app` MIME type, and `_meta.ui.resourceUri` on the tool definition.
- Frameworks that hide the protocol surface behind proprietary abstractions MUST NOT be
  adopted for the graded paths, because they make compliance unverifiable by inspection.
- Every protocol claim MUST be demonstrable from observed output — a network trace or a
  `resources/read` response — not from documentation alone.

*Rationale:* A judge can falsify a false protocol claim in under a minute. A bespoke renderer
that merely resembles A2UI fails the requirement it was built to satisfy.

### II. Zero-Key Demo

A fresh clone with an empty `.env` MUST produce the complete working flow via
`docker compose up`.

- Every external integration MUST degrade to a mock that returns a realistic payload tagged
  `mode: "mock"`.
- Mock output MUST be visible in the UI and visibly distinguished from live output.
- The LLM provider is the only permitted hard dependency; an `echo` provider MUST exist for CI.
- No required-path feature may depend on a credential the evaluator does not have.

*Rationale:* Evaluators run the project without our accounts. A demo that only works on the
author's machine is unverifiable, and notification channels are best-effort by nature — none
may block a booking.

### III. Honest Ranking (NON-NEGOTIABLE)

The recommendation engine MUST be brand-neutral.

- No make, model, or provider may receive a scoring bonus, weight adjustment, tie-break
  preference, or placement override.
- BMW vehicles MAY carry richer attribute data; they MUST NOT rank higher for being BMW.
- Every ranked result MUST expose a per-listing `score_breakdown` with each component's
  contribution.
- Agent explanations MUST cite figures drawn from that breakdown and the listing data.

*Rationale:* The brief requires 10+ brands per category, and the agent's credibility rests
entirely on honest ordering. A weighted scorer is discoverable in source review, and a rigged
recommendation engine reads far worse than a competitor's car placing first.

### IV. Truthful Artifacts

Nothing the system emits may misrepresent what it is.

- The marketplace dataset MUST be labelled synthetic wherever it is presented.
- Payment and reservation artifacts MUST carry an explicit simulated-transaction notice; no
  real payment may be processed.
- Features that are specified but not built MUST be labelled DESIGNED in documentation and
  presentation, never demonstrated as working.
- Interactive controls MUST NOT imply an effect they do not have; an acknowledgement must
  describe only what actually occurred.

*Rationale:* A fabricated receipt or a button that pretends to work is a correctness defect
and a credibility loss. Labelled gaps cost less than discovered ones.

### V. Reproducible Builds

- Dependency versions MUST be pinned exactly. Caret and tilde ranges are prohibited.
- Lockfiles MUST be committed.
- Every declared dependency MUST be verified installable against its registry before it is
  written into a manifest.
- Secrets MUST live only in `.env`, which MUST remain untracked.

*Rationale:* A silent minor-version upgrade mid-build is a class of failure a two-day project
cannot absorb, and several ecosystem packages here publish canary releases aggressively.

### VI. Scope Discipline

All work MUST be tiered:

- **SHIP** — required by the brief or by the demo narrative. Non-negotiable.
- **STRETCH** — built only if the SHIP tier is green at the stated checkpoint.
- **DESIGNED** — specified and presented as architecture; not built.

Rules:

- Schedule overrun MUST land on STRETCH items and MUST NOT reduce a graded requirement.
- Containerization, README, slide deck, and video demo are SHIP and MUST NOT be reclassified.
- A checkpoint that fails MUST cause the following STRETCH block to be skipped, not compressed.
- Timeboxed items MUST have a predetermined fallback that is executed when the box expires.

*Rationale:* The realistic work estimate exceeds the available window. Tiering decides in
advance what gives way, so the decision is not made under pressure at the deadline.

## Technology & Protocol Constraints

- **Agent harness**: LangChain DeepAgents. Exactly one harness; no mixing.
- **MCP App servers**: Python, via `FastMCP` in the MCP Python SDK, mounted in the FastAPI
  application. Two apps are mandatory — form-filling and mock payment — and both MUST render
  inside the chat.
- **Generative UI**: A2UI, pinned to a single specification version matching the renderer.
- **LLM**: Google AI Studio via `langchain-google-genai`. Vertex AI is a different product and
  MUST NOT be referenced as though interchangeable.
- **Marketplace data**: a synthetic in-memory JSON dataset — at least 100 listings, at least 10
  categories, at least 10 distinct brands in each category. This coverage MUST be enforced by an
  automated test, not by inspection.
- **State**: session state MUST persist across interview, research, and recommendation steps,
  keyed by session identifier.
- **Prohibited**: BMW Group APIs, real payment processing, and any integration whose activation
  requires an approval process longer than the build window.

## Development Workflow & Quality Gates

- Work proceeds in small, individually reviewable steps; each is confirmed before the next
  begins.
- `logs/WORKLOG.md` and `logs/DECISIONS.md` MUST be updated as work lands. Reversed decisions
  are appended with their reasoning, never rewritten.
- Commits are incremental and descriptive. Pushing to any remote requires explicit approval.
- Before any dependency is added, its existence and current version MUST be checked against the
  registry.
- Before the demo is recorded, the zero-key path MUST be verified from a clean clone.
- Checkpoint gates defined in the build order are binding; a red checkpoint changes the plan
  rather than the deadline.

## Governance

This constitution supersedes conflicting guidance in `docs/`, `gemini/`, and `claudedocs/`.
Where those documents disagree with it, this file wins and the other document is corrected.

**Amendment procedure.** Amendments MUST be recorded in this file with an updated version, an
entry in the Sync Impact Report, and a corresponding row in `logs/DECISIONS.md` stating the
rationale. Principles marked NON-NEGOTIABLE MUST NOT be weakened during the build window;
they may only be strengthened.

**Versioning policy.** Semantic versioning applies:

- MAJOR — a principle is removed or redefined in a backward-incompatible way.
- MINOR — a principle or section is added, or guidance is materially expanded.
- PATCH — clarification, wording, or non-semantic refinement.

**Compliance review.** Every specification, plan, and task set MUST be checked against these
principles before implementation begins. Any deviation MUST be justified in writing at the
point of deviation. Complexity that serves no graded requirement MUST be removed rather than
justified.

**Version**: 1.0.0 | **Ratified**: 2026-08-08 | **Last Amended**: 2026-08-08
