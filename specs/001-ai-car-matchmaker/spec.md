# Feature Specification: AI Car Matchmaker

**Feature Branch**: `001-ai-car-matchmaker`

**Created**: 2026-08-08

**Status**: Draft

**Input**: A multistep AI agent that interviews a person about buying or renting a car, researches a
marketplace on their behalf, and presents ranked suggestions with explained reasoning — with booking
and mock checkout completed without leaving the conversation.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Tell the agent what I need (Priority: P1)

Someone arrives not knowing which car suits them. Rather than filling in a search form, they have a
conversation. The agent asks what they're trying to do, what kind of vehicle they have in mind, what
they can spend, and when they need it — one thing at a time, adapting to what it already knows. If
they volunteer several answers at once, the agent doesn't ask again.

**Why this priority**: Nothing downstream can happen without these four inputs. This is the
foundation of every other story.

**Independent Test**: Hold a conversation from a cold start and confirm all four inputs are captured
and visible; deliver the same information in a different order and confirm no question is repeated.

**Acceptance Scenarios**:

1. **Given** a new conversation, **When** the person says "I need something for weekend camping
   trips", **Then** the agent infers a likely category and confirms it rather than asking from scratch.
2. **Given** a person who says "renting an SUV under $900 for the week of September 3rd", **When**
   the message is processed, **Then** all four inputs are captured from that single message and the
   agent moves on to research.
3. **Given** an incomplete interview, **When** the person asks to see cars anyway, **Then** the agent
   states which input is still missing and offers to proceed with a stated assumption.
4. **Given** a captured budget, **When** the person later says "actually make it $1,200", **Then**
   the stored budget is revised and prior results are recomputed.

---

### User Story 2 - See ranked options and understand why (Priority: P1)

The person receives a shortlist. Each suggestion says plainly why it is there and what it costs them
relative to the alternatives — not a match percentage alone, but a comparison in the terms a buyer
actually weighs: range, charging time, running costs, safety, acceleration, price.

**Why this priority**: This is the product's core claim. A shortlist without reasoning is a search
results page.

**Independent Test**: Complete an interview and confirm every returned option carries a per-option
reasoning breakdown whose figures match the underlying listing data.

**Acceptance Scenarios**:

1. **Given** a completed interview, **When** research finishes, **Then** the person sees a ranked
   shortlist where each entry states its overall fit and the contribution of each factor.
2. **Given** a ranked shortlist, **When** the person reads the top suggestion, **Then** its
   explanation cites at least one concrete figure in favour and at least one trade-off against.
3. **Given** two vehicles from different manufacturers with equivalent attributes, **When** they are
   ranked, **Then** neither is ordered ahead of the other on the basis of its brand.
4. **Given** a target date, **When** a vehicle is unavailable on that date, **Then** it is either
   excluded or shown with its availability gap stated.
5. **Given** a shortlist, **When** the person asks "why not something cheaper?", **Then** the agent
   answers using the same factors it ranked on.

---

### User Story 3 - Book and pay without leaving the conversation (Priority: P1)

Having chosen, the person completes their details and a simulated payment inside the conversation
itself. They never navigate away, and it is unmistakable throughout that no real money moves.

**Why this priority**: A mandatory requirement of the challenge, and the point at which the
experience becomes a product rather than a demo.

**Independent Test**: Select a vehicle, complete both steps in-conversation, and confirm a booking
record exists and no external page was opened.

**Acceptance Scenarios**:

1. **Given** a selected vehicle, **When** the person chooses to book, **Then** a form appears within
   the conversation and its submitted values are available to the agent.
2. **Given** a completed booking form, **When** the person proceeds to payment, **Then** a checkout
   appears in the conversation showing an itemised total — base price, delivery charge, options, tax
   — and offers finance, lease and outright alternatives.
3. **Given** a payment step, **When** it is displayed, **Then** it states clearly that the
   transaction is simulated.
4. **Given** a submitted payment, **When** it completes, **Then** a confirmation with a reference is
   shown and the booking is recorded against the session.
5. **Given** an abandoned form, **When** the person returns, **Then** their partially entered values
   are still present.

---

### User Story 4 - Watch the agent work (Priority: P2)

While the agent researches, the person sees what it is doing — how many listings were considered,
how many survived filtering, what it is ranking on — rather than an indeterminate spinner.

**Why this priority**: Directly required, and it is what makes a multistep agent legible instead of
opaque. Independent of the shortlist itself.

**Independent Test**: Trigger a search and confirm progress steps appear sequentially and reflect
real counts from the search, not a scripted animation.

**Acceptance Scenarios**:

1. **Given** research has begun, **When** each stage completes, **Then** a corresponding step appears
   with figures drawn from the actual search.
2. **Given** a search returning no matches, **When** it completes, **Then** the person is told which
   constraint eliminated everything and offered a specific relaxation.
3. **Given** the interview in progress, **When** an input is captured, **Then** the displayed
   interview state updates to reflect it.

---

### User Story 5 - Receive the shortlist and confirmation outside the conversation (Priority: P2)

The person gets a written comparison they can re-read later, and a confirmation when they book. The
dealer is alerted to a serious enquiry at the same moment.

**Why this priority**: Extends value past the session and demonstrates the dealer-facing half. Not
required for the core journey to succeed.

**Independent Test**: Complete a booking and confirm each configured recipient received exactly one
correctly populated message.

**Acceptance Scenarios**:

1. **Given** a shortlist and a supplied address, **When** ranking completes, **Then** a comparison of
   the top options is sent whose figures match those shown in the conversation.
2. **Given** a confirmed booking, **When** it completes, **Then** a confirmation is delivered stating
   it is a simulated reservation.
3. **Given** a high-scoring match, **When** ranking completes, **Then** an internal alert is raised
   containing the person's stated needs, the top match, and the agent's reasoning.
4. **Given** a delivery attempt that fails, **When** the failure occurs, **Then** it is recorded and
   the person's booking still completes.
5. **Given** the same event occurring twice, **When** delivery is attempted, **Then** exactly one
   message is sent.
6. **Given** no delivery credentials are configured, **When** an event fires, **Then** the message is
   still produced and shown as clearly simulated.

---

### User Story 6 - Pick up where I left off (Priority: P3)

Someone who steps away — or who began elsewhere — returns via a link and finds everything they
already said still there.

**Why this priority**: The clearest demonstration of memory across a session boundary, but the core
journey works without it.

**Independent Test**: Capture inputs, obtain a resume link, open it in a fresh browser session, and
confirm every input and result is intact.

**Acceptance Scenarios**:

1. **Given** an in-progress session, **When** a resume link is opened in a new browser session,
   **Then** all captured inputs and any shortlist are restored.
2. **Given** a restored session, **When** the person continues, **Then** the agent does not re-ask
   anything already answered.
3. **Given** an expired or already-used link, **When** it is opened, **Then** the person is told it
   is no longer valid and offered a fresh start.

---

### User Story 7 - Inspect how a recommendation was reached (Priority: P3)

Someone evaluating the system can trace a completed session end to end — each reasoning step, each
tool call, each timing — and assess the quality of the explanations produced.

**Why this priority**: Valuable for evaluation and debugging; no user-facing behaviour depends on it.

**Independent Test**: Complete a session, then reconstruct its full decision path from the recorded
trace alone.

**Acceptance Scenarios**:

1. **Given** a completed session, **When** its trace is examined, **Then** every reasoning step and
   tool call appears in order with timings.
2. **Given** a set of recorded sessions, **When** they are scored, **Then** input-capture accuracy
   and explanation quality are reported per session.

---

### Edge Cases

- A stated budget matches nothing in the marketplace.
- A target date is in the past, or beyond any listed availability.
- The person changes intent mid-session — from renting to buying — after a shortlist exists.
- Contradictory input in one message ("cheap luxury supercar under $10,000").
- A vehicle is selected, then becomes unavailable before booking completes.
- The person abandons mid-checkout and returns after the reservation hold has lapsed.
- Free-text input names a category or manufacturer absent from the marketplace.
- The conversation is nonsensical or unrelated to vehicles.
- Notification delivery fails while the booking itself succeeds.
- The same booking is submitted twice in quick succession.
- No contact address was ever supplied, but an out-of-band message is due.

## Requirements *(mandatory)*

### Functional Requirements

**Interview**

- **FR-001**: System MUST capture, through conversation, whether the person intends to buy or rent.
- **FR-002**: System MUST capture a vehicle category, a budget, and a target date.
- **FR-003**: System MUST extract multiple inputs from a single message when they are present, and
  MUST NOT re-ask anything already captured.
- **FR-004**: System MUST allow any captured input to be revised at any point, and MUST recompute
  affected results when one changes.
- **FR-005**: System MUST show the person which inputs are captured and which remain outstanding.
- **FR-006**: System MUST state its assumption explicitly when proceeding with an input missing.

**Research and ranking**

- **FR-007**: System MUST search a marketplace of at least 100 vehicles spanning at least 12
  categories with at least 10 distinct manufacturers in every category.
- **FR-008**: System MUST filter on the captured inputs, including availability on the target date.
- **FR-009**: System MUST rank surviving vehicles by a weighted score whose components are recorded
  individually per vehicle.
- **FR-010**: System MUST NOT apply any manufacturer-, model-, or supplier-specific adjustment to
  ranking. Ordering MUST be reproducible from the recorded components alone.
- **FR-011**: System MUST accompany each recommendation with reasoning citing at least one concrete
  figure supporting it and at least one trade-off against it.
- **FR-012**: System MUST report which constraint eliminated all candidates when nothing matches, and
  offer a specific relaxation.
- **FR-013**: System MUST answer follow-up questions about its ranking using the same components it
  ranked on.

**Booking and payment**

- **FR-014**: System MUST present a details form within the conversation and make its values
  available to the agent.
- **FR-015**: System MUST present a checkout within the conversation showing an itemised total and
  alternative purchase arrangements.
- **FR-016**: System MUST state on every payment and confirmation artifact that the transaction is
  simulated, and MUST NOT process real payment or collect real payment credentials.
- **FR-017**: System MUST record a booking against the session with a reference on completion.
- **FR-018**: System MUST preserve partially entered form values across an interruption.

**Progress and presentation**

- **FR-019**: System MUST display research progress as discrete steps carrying real figures from the
  work performed.
- **FR-020**: System MUST render the catalogue and progress as agent-authored dynamic components,
  determined at runtime rather than fixed in advance.

**State**

- **FR-021**: System MUST retain all captured inputs, results, and booking state for the life of a
  session, across interview, research, and recommendation.
- **FR-022**: System MUST record which channel supplied each captured input.
- **FR-023**: System MUST allow a session to be resumed from a single-use, time-limited link, and
  MUST reject an expired or spent link with a clear explanation.

**Notifications**

- **FR-024**: System MUST dispatch notifications on ranking completion and booking confirmation
  through one shared mechanism.
- **FR-025**: System MUST send exactly one message per recipient per event, however many times the
  event is raised.
- **FR-026**: System MUST record delivery failures without interrupting the person's journey.
- **FR-027**: System MUST produce and display the message content even when delivery is not
  configured, marked unmistakably as simulated.
- **FR-028**: System MUST ensure figures in any out-of-band message match those shown in the
  conversation.

**Operation**

- **FR-029**: System MUST run its complete journey with no third-party credentials supplied beyond
  the language model.
- **FR-030**: System MUST label the marketplace dataset as synthetic wherever it is presented.
- **FR-031**: System MUST present capabilities that are specified but not built as designs, never as
  working features.

### Mandated Constraints

Fixed by the challenge, not chosen by the team, and therefore stated as requirements:

- **MC-001**: The details form and the payment interface MUST each be delivered as MCP Apps rendered
  inside the conversation.
- **MC-002**: The catalogue and live progress MUST be driven by the A2UI protocol in its published
  wire format — not static markup, and not a bespoke substitute.
- **MC-003**: The agent MUST be built on a recognised multistep agent harness.
- **MC-004**: No manufacturer-proprietary vehicle APIs may be used.
- **MC-005**: The system MUST be runnable as a container, or reachable as a deployed application.

### Key Entities

- **Session**: One person's journey. Holds captured inputs, their originating channel, the shortlist,
  the selection, booking state, and a delivery log. Identified for resumption.
- **Listing**: A vehicle offered for sale or hire. Carries identity and specification, purchase and
  hire pricing, features, performance, electric-range and charging attributes where applicable,
  safety ratings, five-year running-cost estimates, availability windows, and its supplier.
- **Category**: A marketplace grouping. Every category holds listings from at least 10 manufacturers.
- **Ranked Result**: A listing paired with its overall score, the individual contribution of each
  ranking factor, and the reasoning presented to the person.
- **Booking**: A simulated reservation — the chosen listing, submitted details, itemised pricing,
  reference, and status.
- **Notification**: One delivery attempt — its event, recipient, channel, rendered content, outcome,
  and whether it was simulated.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A person reaching the system cold obtains a ranked, explained shortlist within 3
  minutes of conversation.
- **SC-002**: Every recommendation carries reasoning citing at least one supporting figure and one
  trade-off, in 100% of sessions.
- **SC-003**: The marketplace contains at least 100 vehicles, at least 12 categories, and at least 10
  manufacturers per category — verified automatically rather than by inspection.
- **SC-004**: Booking and simulated payment complete without the person leaving the conversation, in
  100% of attempts.
- **SC-005**: A person supplying all four inputs in one message is asked no redundant question.
- **SC-006**: Ranking order is unchanged when manufacturer names are masked from the ranking inputs.
- **SC-007**: A session resumed from a link retains 100% of captured inputs and results.
- **SC-008**: The complete journey succeeds from a clean installation with no third-party credentials
  beyond the language model.
- **SC-009**: Repeating an event produces exactly one message per recipient.
- **SC-010**: Research progress becomes visible within 2 seconds of research beginning, and each step
  reflects real work performed.
- **SC-011**: A completed session's decision path is fully reconstructable from its recorded trace.
- **SC-012**: No artifact leaving the system implies a real transaction or real inventory.

## Assumptions

- **Single anonymous user per session.** No accounts, sign-in, or roles; the challenge places
  authentication out of scope. A resume link therefore acts as a capability URL, single-use and
  time-limited.
- **Contact details are optional during the interview and required at booking.** If ranking completes
  before any address is known, the comparison is prepared and shown in-conversation, and sent only
  once an address exists. This avoids blocking the shortlist behind a details request.
- **Hire pricing is quoted per day**, with the total for the stated period shown alongside it. Budget
  matching for hire compares against the period total.
- **The shortlist is the top three to five vehicles.** Enough to compare meaningfully, few enough to
  read.
- **A target date means a single date**, not a range, for both purchase and hire; hire duration is
  captured separately when the person supplies it.
- **The marketplace is synthetic and fixed at build time.** No live inventory, no price movement, and
  therefore no genuine price-drop events.
- **Marketplace data is invented but internally consistent.** Figures are plausible and mutually
  coherent; they are not claimed to be accurate to any real vehicle.
- **Session state lives only for the session.** Durable storage is out of scope.
- **English only.**
- **Notifications are best-effort.** No required step may depend on one succeeding.
- **Tiering is inherited from the project constitution.** Stories 1–5 are SHIP; story 6 is SHIP for
  its web path and DESIGNED for other channels; story 7 is STRETCH.
