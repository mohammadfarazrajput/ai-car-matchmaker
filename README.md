# AI Car Matchmaker

**Amulate Summer Hackathon 2026**

A multistep AI agent that helps users find the right car to rent or buy through interactive interviews, marketplace research, and ranked recommendations.

> **Status: pre-implementation.** This repository currently contains specifications only.
> The Quick Start below describes the target state, not what runs today.
> **[docs/PLAN.md](docs/PLAN.md) is the authoritative build plan** — it corrects several
> details in the other documents (dependency versions, data model, MCP Apps host).

---

## Features

- **Interactive Interview**: Conversational flow to capture user preferences
- **Marketplace Research**: Search 100+ car listings across 10+ categories
- **Smart Recommendations**: AI-ranked suggestions with explanations
- **Rich UI**: A2UI-powered car cards and dynamic interfaces
- **MCP Apps**: In-chat form-filling and mock payment
- **Multi-Channel Communication**: Email, SMS, Voice, Slack, WhatsApp
- **Voice Support**: Speech-to-text and text-to-speech via Deepgram

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Agent Framework | LangChain DeepAgents |
| Transport | AG-UI (Python) |
| Generative UI | A2UI + CopilotKit |
| Backend | FastAPI |
| Frontend | Next.js + React |
| Primary LLM | Google Vertex AI (Gemini 2.5 Flash) |
| Fallback LLM | Groq (Llama 3.3 70B) |
| STT/TTS | Deepgram Nova-3 / Aura |
| Email | SendGrid |
| SMS/Voice | Twilio |
| Deployment | Docker |

---

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- API keys (see below)

### 1. Clone Repository

```bash
git clone https://github.com/your-username/ai-car-matchmaker.git
cd ai-car-matchmaker
```

### 2. Setup Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
```

### 3. Setup Frontend

```bash
cd frontend
npm install
```

### 4. Run

```bash
# Terminal 1 - Backend
cd backend
uvicorn app.main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### 5. Open Browser

Navigate to `http://localhost:3000`

---

## API Keys

You'll need API keys for the following services:

| Service | Provider | Free Tier | Get Key |
|---------|----------|-----------|---------|
| LLM | Google Vertex AI | 1,000 RPD | [console.cloud.google.com](https://console.cloud.google.com) |
| LLM Fallback | Groq | 1,000 RPD | [console.groq.com](https://console.groq.com) |
| STT/TTS | Deepgram | $200 credits | [console.deepgram.com](https://console.deepgram.com) |
| Email | SendGrid | 100/day | [app.sendgrid.com](https://app.sendgrid.com) |
| SMS/Voice | Twilio | 100 SMS, 75 min | [console.twilio.com](https://console.twilio.com) |
| Slack | Slack | Free | [api.slack.com](https://api.slack.com/apps) |

---

## Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build
```

---

## Project Structure

```
ai-car-matchmaker/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── agent/
│   │   ├── tools/
│   │   ├── mcp/
│   │   ├── speech/
│   │   ├── data/
│   │   └── models/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   ├── components/
│   │   └── lib/
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
├── README.md
└── docs/
    ├── PLAN.md
    ├── SPEC.md
    ├── ARCHITECTURE.md
    ├── TASKS.md
    └── IMPLEMENTATION.md
```

---

## Documentation

- **[Build Plan](docs/PLAN.md)** — authoritative; supersedes conflicting details below
- [Project Specification](docs/SPEC.md)
- [System Architecture](docs/ARCHITECTURE.md)
- [Task Breakdown](docs/TASKS.md)
- [Implementation Guide](docs/IMPLEMENTATION.md)

---

## How It Works

1. **Interview**: User tells the agent what they need (buy/rent, car type, budget, date)
2. **Research**: Agent searches the marketplace for matching cars
3. **Recommend**: Agent presents top matches with explanations
4. **Book**: User selects a car and completes booking via MCP Apps
5. **Notify**: Confirmations sent via Email, SMS, WhatsApp, and Slack

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

---

## License

MIT License

---

## Acknowledgments

- [LangChain DeepAgents](https://github.com/langchain-ai/deepagents)
- [A2UI Protocol](https://a2ui.org)
- [CopilotKit](https://copilotkit.ai)
- [MCP Protocol](https://modelcontextprotocol.io)
