# AI Car Matchmaker - System Architecture

---

## 1. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          USER INTERFACES                                │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐   │
│  │ Web UI       │ │ Voice Input  │ │ Slack Bot    │ │ WhatsApp     │   │
│  │ (Next.js)    │ │ (WebRTC)     │ │              │ │              │   │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         AG-UI TRANSPORT                                 │
│                    (SSE - Server-Sent Events)                           │
└─────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        BACKEND SERVICES                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │                    FastAPI Application                               ││
│  │  ┌───────────────────────────────────────────────────────────────┐  ││
│  │  │              LangChain DeepAgents Graph                       │  ││
│  │  │                                                               │  ││
│  │  │  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐   │  ││
│  │  │  │Interview│───▶│Research │───▶│Recommend│───▶│ Booking │   │  ││
│  │  │  │ Agent   │    │ Agent   │    │ Agent   │    │ Agent   │   │  ││
│  │  │  └─────────┘    └─────────┘    └─────────┘    └─────────┘   │  ││
│  │  │       │              │              │              │          │  ││
│  │  │       ▼              ▼              ▼              ▼          │  ││
│  │  │  ┌─────────────────────────────────────────────────────┐     │  ││
│  │  │  │              Tool Layer                              │     │  ││
│  │  │  │  ┌──────────┐ ┌──────────┐ ┌──────────┐           │     │  ││
│  │  │  │  │Marketplace│ │A2UI Gen  │ │MCP Apps  │           │     │  ││
│  │  │  │  │ Tools    │ │ Tools    │ │          │           │     │  ││
│  │  │  │  └──────────┘ └──────────┘ └──────────┘           │     │  ││
│  │  │  └─────────────────────────────────────────────────────┘     │  ││
│  │  └───────────────────────────────────────────────────────────────┘  ││
│  │                                                                     ││
│  │  ┌───────────────────────────────────────────────────────────────┐  ││
│  │  │              Communication Services                           │  ││
│  │  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌────────┐│  ││
│  │  │  │ Email   │ │ SMS     │ │ Voice   │ │ Slack   │ │WhatsApp││  ││
│  │  │  │SendGrid │ │ Twilio  │ │ Twilio  │ │ API     │ │ Meta   ││  ││
│  │  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └────────┘│  ││
│  │  └───────────────────────────────────────────────────────────────┘  ││
│  │                                                                     ││
│  │  ┌───────────────────────────────────────────────────────────────┐  ││
│  │  │              Speech Services                                  │  ││
│  │  │  ┌─────────────────┐ ┌─────────────────┐                     │  ││
│  │  │  │ Deepgram STT    │ │ Deepgram TTS    │                     │  ││
│  │  │  │ (Nova-3/Whisper)│ │ (Aura)          │                     │  ││
│  │  │  └─────────────────┘ └─────────────────┘                     │  ││
│  │  └───────────────────────────────────────────────────────────────┘  ││
│  └─────────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        EXTERNAL SERVICES                                │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐       │
│  │ Google      │ │ Groq        │ │ Deepgram    │ │ Twilio      │       │
│  │ Vertex AI   │ │             │ │             │ │             │       │
│  │ (Gemini)    │ │ (Llama)     │ │ (STT/TTS)   │ │ (SMS/Voice) │       │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘       │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐                       │
│  │ SendGrid    │ │ Slack       │ │ Meta        │                       │
│  │ (Email)     │ │ (Messaging) │ │ (WhatsApp)  │                       │
│  └─────────────┘ └─────────────┘ └─────────────┘                       │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Data Flow

### 2.1 Interview Flow

```
User Input (Text/Voice)
        │
        ▼
┌─────────────────┐
│ Speech-to-Text  │ (if voice input)
│ (Deepgram)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Interview Agent │
│ (State Machine) │
└────────┬────────┘
         │
         ├──▶ Update State (preferences, use case, budget, etc.)
         │
         ▼
┌─────────────────┐
│ A2UI Generator  │
│ (Progress UI)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ AG-UI Transport │
│ (SSE Stream)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ CopilotKit      │
│ (A2UI Render)   │
└────────┬────────┘
         │
         ▼
    User Sees Progress
```

### 2.2 Research & Recommendation Flow

```
Interview Complete
        │
        ▼
┌─────────────────┐
│ Research Agent  │
│ (Marketplace)   │
└────────┬────────┘
         │
         ├──▶ Search Mock Marketplace
         ├──▶ Filter by Preferences
         ├──▶ Rank by Relevance
         │
         ▼
┌─────────────────┐
│ Recommend Agent │
│ (Ranking)       │
└────────┬────────┘
         │
         ├──▶ Generate Explanations
         ├──▶ Create A2UI Cards
         │
         ▼
┌─────────────────┐
│ A2UI Car Cards  │
│ (Rich UI)       │
└────────┬────────┘
         │
         ▼
    User Sees Results
```

### 2.3 Booking & Notification Flow

```
User Selects Car
        │
        ▼
┌─────────────────┐
│ MCP Booking App │
│ (Form)          │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ MCP Payment App │
│ (Mock Checkout) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Booking Agent   │
│ (Confirmation)  │
└────────┬────────┘
         │
         ├──▶ Email (SendGrid)
         ├──▶ SMS (Twilio)
         ├──▶ WhatsApp (Meta)
         ├──▶ Slack (Internal)
         │
         ▼
    User Gets Confirmations
```

---

## 3. Component Architecture

### 3.1 Backend Components

```python
# Backend Module Structure
app/
├── main.py                    # FastAPI application
├── config.py                  # Configuration management
├── agent/
│   ├── __init__.py
│   ├── graph.py               # DeepAgents graph definition
│   ├── state.py               # Agent state management
│   ├── interview.py           # Interview agent logic
│   ├── research.py            # Research agent logic
│   ├── recommend.py           # Recommendation agent logic
│   └── booking.py             # Booking agent logic
├── tools/
│   ├── __init__.py
│   ├── marketplace.py         # Marketplace search tools
│   ├── a2ui.py               # A2UI generation tools
│   ├── email_tools.py         # SendGrid integration
│   ├── sms_tools.py           # Twilio SMS
│   ├── voice_tools.py         # Twilio Voice + Deepgram
│   ├── slack_tools.py         # Slack messaging
│   └── whatsapp_tools.py      # WhatsApp Business
├── mcp/
│   ├── __init__.py
│   ├── form_server.py         # Form-filling MCP server
│   ├── payment_server.py      # Mock payment MCP server
│   └── booking_server.py      # Booking confirmation MCP
├── speech/
│   ├── __init__.py
│   ├── deepgram_stt.py        # Speech-to-text
│   ├── deepgram_tts.py        # Text-to-speech
│   └── whisper.py             # Whisper model
├── data/
│   ├── __init__.py
│   ├── listings.json          # 100+ car listings
│   └── categories.json        # Car categories
└── models/
    ├── __init__.py
    └── schemas.py             # Pydantic models
```

### 3.2 Frontend Components

```typescript
// Frontend Module Structure
src/
├── app/
│   ├── layout.tsx             # Root layout
│   ├── page.tsx               # Main page
│   └── api/
│       └── copilotkit/
│           └── route.ts       # CopilotKit API route
├── components/
│   ├── ChatPanel.tsx          # Main chat interface
│   ├── CarCard.tsx            # A2UI car card
│   ├── InterviewProgress.tsx  # Interview progress indicator
│   ├── PaymentForm.tsx        # Payment form
│   ├── VoiceInput.tsx         # Voice input component
│   ├── CommunicationPanel.tsx # Email/SMS/Call UI
│   └── ui/                    # Shared UI components
├── lib/
│   ├── a2ui/
│   │   ├── definitions.ts     # A2UI component definitions
│   │   ├── renderers.tsx      # A2UI component renderers
│   │   └── catalog.ts         # A2UI catalog
│   └── api.ts                 # API utilities
└── types/
    └── index.ts               # TypeScript types
```

---

## 4. MCP Apps Architecture

### 4.1 Form-Filling MCP App

```
┌─────────────────────────────────────────┐
│           MCP Form App                  │
├─────────────────────────────────────────┤
│  ┌─────────────────────────────────┐    │
│  │  User Preferences Form          │    │
│  │  ┌─────────────────────────┐    │    │
│  │  │ Use Case: [Buy/Rent]    │    │    │
│  │  │ Car Type: [Dropdown]    │    │    │
│  │  │ Budget: [Range Slider]  │    │    │
│  │  │ Features: [Checkboxes]  │    │    │
│  │  │ Date: [Date Picker]     │    │    │
│  │  └─────────────────────────┘    │    │
│  │  [Submit] [Cancel]              │    │
│  └─────────────────────────────────┘    │
│                                          │
│  Communication: postMessage (MCP)        │
│  Sandboxed: Yes (iframe)                 │
└─────────────────────────────────────────┘
```

### 4.2 Payment MCP App

```
┌─────────────────────────────────────────┐
│           MCP Payment App               │
├─────────────────────────────────────────┤
│  ┌─────────────────────────────────┐    │
│  │  Mock Checkout Form             │    │
│  │  ┌─────────────────────────┐    │    │
│  │  │ Card Number: [****]     │    │    │
│  │  │ Expiry: [MM/YY]         │    │    │
│  │  │ CVV: [***]              │    │    │
│  │  │ Name: [_______]         │    │    │
│  │  └─────────────────────────┘    │    │
│  │  Total: $XXX.XX                 │    │
│  │  [Pay Now] [Cancel]             │    │
│  └─────────────────────────────────┘    │
│                                          │
│  Note: Mock payment - no real processing │
│  Communication: postMessage (MCP)        │
│  Sandboxed: Yes (iframe)                 │
└─────────────────────────────────────────┘
```

---

## 5. State Management

### 5.1 Agent State

```python
class AgentState(TypedDict):
    # Interview State
    use_case: str  # "buy" | "rent"
    car_type: str  # "sedan" | "suv" | "truck" | etc.
    budget_min: float
    budget_max: float
    target_date: str
    location: str
    preferences: List[str]
    
    # Research State
    search_results: List[CarListing]
    ranked_results: List[RankedCar]
    
    # Booking State
    selected_car: CarListing
    booking_details: BookingInfo
    payment_status: str
    
    # Communication State
    notifications_sent: List[Notification]
    
    # Messages
    messages: List[BaseMessage]
```

### 5.2 State Persistence

- In-memory state during session
- LangGraph checkpointer for durability
- Virtual filesystem for long-term memory

---

## 6. API Endpoints

### 6.1 AG-UI Endpoint

```
POST /agent
├── Purpose: Main agent endpoint
├── Protocol: AG-UI (SSE)
├── Events: RUN_STARTED, TEXT_MESSAGE_*, TOOL_CALL_*, STATE_*
└── Returns: SSE stream of agent events
```

### 6.2 MCP Endpoints

```
POST /mcp/form
├── Purpose: Form-filling MCP App
├── Protocol: MCP (JSON-RPC)
└── Returns: HTML resource

POST /mcp/payment
├── Purpose: Mock payment MCP App
├── Protocol: MCP (JSON-RPC)
└── Returns: HTML resource

POST /mcp/booking
├── Purpose: Booking confirmation MCP App
├── Protocol: MCP (JSON-RPC)
└── Returns: HTML resource
```

### 6.3 Utility Endpoints

```
GET /health
├── Purpose: Health check
└── Returns: {"status": "ok"}

GET /api/listings
├── Purpose: Get car listings
└── Returns: List[CarListing]

POST /api/voice
├── Purpose: Voice input processing
└── Returns: Transcribed text
```

---

## 7. Security Architecture

### 7.1 API Key Management

- All keys stored in environment variables
- Never committed to repository
- Rotated regularly in production

### 7.2 MCP App Security

- Sandboxed iframes
- PostMessage communication only
- No access to parent DOM
- CSP headers enforced

### 7.3 Data Privacy

- No real payment data processed
- User data stored in-memory only
- No persistence to external databases
- GDPR-compliant data handling

---

## 8. Deployment Architecture

### 8.1 Docker Compose

```yaml
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - GROQ_API_KEY=${GROQ_API_KEY}
      - DEEPGRAM_API_KEY=${DEEPGRAM_API_KEY}
      - SENDGRID_API_KEY=${SENDGRID_API_KEY}
      - TWILIO_SID=${TWILIO_SID}
      - TWILIO_AUTH_TOKEN=${TWILIO_AUTH_TOKEN}
      - SLACK_BOT_TOKEN=${SLACK_BOT_TOKEN}
    
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
```

### 8.2 Cloud Deployment

- **Frontend**: Vercel / Netlify
- **Backend**: Railway / Render / Google Cloud Run
- **Database**: In-memory (no external DB needed)

---

*Document Version: 1.0*
*Last Updated: August 2026*
