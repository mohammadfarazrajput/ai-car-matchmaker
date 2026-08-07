# AI Car Matchmaker - Project Specification

## Amulate Summer Hackathon 2026

---

## 1. Project Overview

**AI Car Matchmaker** is a multistep AI agent that helps users find the right car to rent or buy. The agent interviews users interactively, researches car marketplaces, and presents ranked, explained suggestions - all within a conversational UI with rich generative interfaces.

### 1.1 Objectives

- Build a multistep AI agent for car buying/renting assistance
- Implement interactive interview flow for user preferences
- Research and rank car options across marketplaces
- Provide rich, dynamic UI using A2UI protocol
- Integrate multiple communication channels (Email, SMS, Voice, Slack, WhatsApp)
- Implement speech-to-text and text-to-speech capabilities
- Deploy as a production-ready application

---

## 2. Functional Requirements

### 2.1 Interview Agent

| Requirement | Description |
|-------------|-------------|
| Interactive Interview | Conversational flow to capture user preferences |
| Use Case Detection | Determine buy vs. rent intent |
| Car Type Selection | Sedan, SUV, Truck, Electric, Luxury, Sports, Hybrid, Van, Coupe, Convertible |
| Budget Range | Flexible budget input with validation |
| Target Date | Purchase/rental date with calendar support |
| Location | User location for nearby marketplace search |
| Preferences | Features, brand preferences, fuel type, etc. |

### 2.2 Marketplace Research

| Requirement | Description |
|-------------|-------------|
| Mock Marketplace | 100+ car listings across 10+ categories |
| Category Coverage | 10+ brands per category |
| Search & Filter | Real-time search with multiple filters |
| Ranking Algorithm | Price, features, availability, user preferences |
| Explanation | Agent explains reasoning behind each suggestion |

### 2.3 Recommendations

| Requirement | Description |
|-------------|-------------|
| Ranked Results | Top matches sorted by relevance |
| A2UI Car Cards | Rich, interactive car listing cards |
| Comparison | Side-by-side car comparison |
| Details View | Expandable car details with images |
| Action Buttons | Book, Save, Share, Get Directions |

### 2.4 MCP Apps (Required)

| MCP App | Purpose |
|---------|---------|
| Form-Filling App | Capture detailed user preferences |
| Payment App | Mock checkout interface |
| Booking App | Booking confirmation and details |

### 2.5 Communication Channels

| Channel | Provider | Use Case |
|---------|----------|----------|
| Email | SendGrid | Booking confirmations, receipts, newsletters |
| SMS | Twilio | Appointment reminders, booking alerts |
| Voice Call | Twilio | Customer support, verification calls |
| Slack | Slack API | Internal team notifications |
| WhatsApp | Meta Business API | Customer inquiries, quick updates |

### 2.6 Speech Features

| Feature | Provider | Use Case |
|---------|----------|----------|
| Speech-to-Text | Deepgram Nova-3 | Voice commands, call transcription |
| Whisper STT | Deepgram Whisper Cloud | High-accuracy transcription |
| Text-to-Speech | Deepgram Aura | Voice responses, call automation |

---

## 3. Non-Functional Requirements

### 3.1 Performance

- Response time < 2 seconds for text responses
- Voice latency < 500ms for real-time conversation
- Support 10+ concurrent users

### 3.2 Scalability

- Horizontal scaling capability
- Stateless agent design
- Database connection pooling

### 3.3 Security

- API key management via environment variables
- MCP Apps run in sandboxed iframes
- No real payment data processed
- HTTPS everywhere

### 3.4 Usability

- Mobile-responsive design
- Accessible UI components
- Clear error messages
- Progress indicators for long operations

---

## 4. Technology Stack

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Agent Framework | LangChain DeepAgents | Free, open-source, built-in subagents |
| Transport | AG-UI (Python) | Native LangGraph integration |
| Generative UI | A2UI + CopilotKit | Declarative UI protocol |
| Backend | FastAPI | High-performance, async support |
| Frontend | Next.js + React | CopilotKit integration |
| Primary LLM | Google Vertex AI (Gemini 2.5 Flash) | Free tier, excellent tool calling |
| Fallback LLM | Groq (Llama 3.3 70B) | Ultra-fast inference |
| STT | Deepgram Nova-3 / Whisper | $200 free credits |
| TTS | Deepgram Aura | $200 free credits |
| Email | SendGrid | 100 emails/day free trial |
| SMS/Voice | Twilio | 100 SMS, 75 min free trial |
| Slack | Slack API | Free for workspaces |
| WhatsApp | Meta Business API | Per-message pricing |
| Deployment | Docker + Cloud | Portable, scalable |

---

## 5. Mock Data Requirements

### 5.1 Car Listings

- **Total Listings**: 100+ cars
- **Categories**: 10+ (Sedan, SUV, Truck, Electric, Luxury, Sports, Hybrid, Van, Coupe, Convertible)
- **Brands per Category**: 10+ (Toyota, Honda, BMW, Tesla, Ford, Mercedes, Audi, Porsche, Lamborghini, Ferrari, etc.)

### 5.2 Listing Fields

```json
{
  "id": "string",
  "make": "string",
  "model": "string",
  "year": "number",
  "category": "string",
  "price": {
    "buy": "number",
    "rent_per_day": "number"
  },
  "features": ["string"],
  "mileage": "number",
  "fuel_type": "string",
  "transmission": "string",
  "seats": "number",
  "image_url": "string",
  "available": "boolean",
  "location": "string",
  "description": "string"
}
```

---

## 6. Success Criteria

### 6.1 Must Have

- [ ] Working interview agent with state management
- [ ] Mock marketplace with 100+ listings
- [ ] A2UI car cards rendering correctly
- [ ] MCP Apps for form-filling and payment
- [ ] At least one communication channel working
- [ ] Docker deployment working

### 6.2 Should Have

- [ ] Multiple communication channels
- [ ] Speech-to-text integration
- [ ] Text-to-speech integration
- [ ] Voice input UI
- [ ] Slack integration for internal notifications

### 6.3 Nice to Have

- [ ] WhatsApp integration
- [ ] Video call support
- [ ] Multi-language support
- [ ] Analytics dashboard

---

## 7. Constraints

- No real payments processed (mock only)
- No BMW Group APIs provided
- Must use free tiers where possible
- Must be containerized with Docker
- Code must be committed to public GitHub repository

---

## 8. Out of Scope

- Real payment processing
- Actual car dealership integration
- User authentication/authorization
- Database persistence (in-memory state)
- Mobile native apps

---

*Document Version: 1.0*
*Last Updated: August 2026*
