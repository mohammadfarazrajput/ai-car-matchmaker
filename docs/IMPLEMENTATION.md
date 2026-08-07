# AI Car Matchmaker - Implementation Guide

---

## 1. Project Setup

### 1.1 Prerequisites

- Python 3.11+
- Node.js 18+
- Docker (optional)
- API Keys (see `.env.example`)

### 1.2 Clone Repository

```bash
git clone https://github.com/your-username/ai-car-matchmaker.git
cd ai-car-matchmaker
```

---

## 2. Backend Implementation

### 2.1 Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── graph.py
│   │   ├── state.py
│   │   ├── interview.py
│   │   ├── research.py
│   │   ├── recommend.py
│   │   └── booking.py
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── marketplace.py
│   │   ├── a2ui.py
│   │   ├── email_tools.py
│   │   ├── sms_tools.py
│   │   ├── voice_tools.py
│   │   ├── slack_tools.py
│   │   └── whatsapp_tools.py
│   ├── mcp/
│   │   ├── __init__.py
│   │   ├── form_server.py
│   │   ├── payment_server.py
│   │   └── booking_server.py
│   ├── speech/
│   │   ├── __init__.py
│   │   ├── deepgram_stt.py
│   │   ├── deepgram_tts.py
│   │   └── whisper.py
│   ├── data/
│   │   ├── __init__.py
│   │   ├── listings.json
│   │   └── categories.json
│   └── models/
│       ├── __init__.py
│       └── schemas.py
├── requirements.txt
├── Dockerfile
└── .env.example
```

### 2.2 Requirements

```txt
# backend/requirements.txt
fastapi>=0.104.0
uvicorn>=0.24.0
pydantic>=2.5.0
pydantic-settings>=2.1.0
langchain>=0.3.0
langchain-core>=0.3.0
langchain-google-genai>=2.0.0
langgraph>=0.2.0
deepagents>=0.7.0
ag-ui-langgraph>=0.1.0
copilotkit>=1.61.0
sendgrid>=6.11.0
twilio>=9.0.0
deepgram-sdk>=3.0.0
httpx>=0.25.0
python-dotenv>=1.0.0
```

### 2.3 Configuration

```python
# app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # LLM
    google_api_key: str
    groq_api_key: str = ""
    
    # Speech
    deepgram_api_key: str = ""
    
    # Email
    sendgrid_api_key: str = ""
    sendgrid_from_email: str = "noreply@car-matchmaker.ai"
    
    # SMS/Voice
    twilio_sid: str = ""
    twilio_auth_token: str = ""
    twilio_phone_number: str = ""
    
    # Slack
    slack_bot_token: str = ""
    slack_channel: str = "#car-bookings"
    
    # WhatsApp
    whatsapp_token: str = ""
    whatsapp_phone_number: str = ""
    
    # App
    backend_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:3000"
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### 2.4 Main Application

```python
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ag_ui_langgraph import add_langgraph_fastapi_endpoint
from app.agent.graph import create_agent_graph
from app.config import settings

app = FastAPI(title="AI Car Matchmaker")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

graph = create_agent_graph()
add_langgraph_fastapi_endpoint(app, graph, "/agent")

@app.get("/health")
async def health():
    return {"status": "ok"}
```

### 2.5 Agent Graph

```python
# app/agent/graph.py
from deepagents import create_deep_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents.middleware import CopilotKitMiddleware
from app.config import settings

def create_agent_graph():
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=settings.google_api_key,
        temperature=0.7,
    )
    
    tools = []  # Add tools here
    
    system_prompt = """You are an AI Car Matchmaker assistant.
    Help users find the right car to rent or buy.
    Interview them about preferences, research marketplace, and recommend options.
    Use A2UI to display car cards when showing results."""
    
    agent = create_deep_agent(
        model=llm,
        tools=tools,
        system_prompt=system_prompt,
        middleware=[CopilotKitMiddleware()],
    )
    
    return agent
```

### 2.6 Marketplace Tools

```python
# app/tools/marketplace.py
import json
from pathlib import Path
from typing import List, Optional
from langchain.tools import tool

LISTINGS_PATH = Path(__file__).parent.parent / "data" / "listings.json"

def load_listings():
    with open(LISTINGS_PATH) as f:
        return json.load(f)

@tool
def search_cars(
    car_type: Optional[str] = None,
    max_price: Optional[float] = None,
    use_case: Optional[str] = None,
    features: Optional[List[str]] = None,
) -> str:
    """Search for cars based on filters. Returns matching car listings."""
    listings = load_listings()
    results = listings
    
    if car_type:
        results = [c for c in results if c["category"].lower() == car_type.lower()]
    if max_price and use_case == "rent":
        results = [c for c in results if c["price"]["rent_per_day"] <= max_price]
    elif max_price:
        results = [c for c in results if c["price"]["buy"] <= max_price]
    
    return json.dumps(results[:10])
```

### 2.7 Email Tools

```python
# app/tools/email_tools.py
from langchain.tools import tool
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from app.config import settings

@tool
def send_email(to_email: str, subject: str, body: str) -> str:
    """Send an email notification to the user."""
    if not settings.sendgrid_api_key:
        return "Email service not configured"
    
    message = Mail(
        from_email=settings.sendgrid_from_email,
        to_emails=to_email,
        subject=subject,
        html_content=body,
    )
    
    try:
        sg = SendGridAPIClient(settings.sendgrid_api_key)
        sg.send(message)
        return f"Email sent successfully to {to_email}"
    except Exception as e:
        return f"Failed to send email: {str(e)}"
```

### 2.8 SMS Tools

```python
# app/tools/sms_tools.py
from langchain.tools import tool
from twilio.rest import Client
from app.config import settings

@tool
def send_sms(to_phone: str, message: str) -> str:
    """Send an SMS notification to the user."""
    if not settings.twilio_sid:
        return "SMS service not configured"
    
    client = Client(settings.twilio_sid, settings.twilio_auth_token)
    
    try:
        sms = client.messages.create(
            body=message,
            from_=settings.twilio_phone_number,
            to=to_phone,
        )
        return f"SMS sent successfully to {to_phone}"
    except Exception as e:
        return f"Failed to send SMS: {str(e)}"
```

### 2.9 Speech-to-Text

```python
# app/speech/deepgram_stt.py
from deepgram import DeepgramClient, PrerecordedOptions
from app.config import settings

async def transcribe_audio(audio_bytes: bytes) -> str:
    """Transcribe audio using Deepgram Nova-3."""
    if not settings.deepgram_api_key:
        return "Speech service not configured"
    
    deepgram = DeepgramClient(settings.deepgram_api_key)
    
    options = PrerecordedOptions(
        model="nova-3",
        smart_format=True,
        language="en",
    )
    
    response = await deepgram.asyncprerecorded.transcribe_file(
        {"buffer": audio_bytes},
        options,
    )
    
    return response["results"]["channels"][0]["alternatives"][0]["transcript"]
```

### 2.10 Text-to-Speech

```python
# app/speech/deepgram_tts.py
from deepgram import DeepgramClient, SpeakOptions
from app.config import settings

def text_to_speech(text: str) -> bytes:
    """Convert text to speech using Deepgram Aura."""
    if not settings.deepgram_api_key:
        return b""
    
    deepgram = DeepgramClient(settings.deepgram_api_key)
    options = SpeakOptions(model="aura-asteria-en")
    
    response = deepgram.synthesis.speak({"text": text}, options)
    return response.stream.read()
```

---

## 3. Frontend Implementation

### 3.1 Requirements

```json
{
  "name": "ai-car-matchmaker-frontend",
  "dependencies": {
    "next": "14.1.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "@copilotkit/react-core": "^1.61.0",
    "@copilotkit/react-ui": "^1.61.0",
    "@copilotkit/a2ui-renderer": "^1.61.0",
    "zod": "^3.22.0"
  },
  "devDependencies": {
    "typescript": "^5.3.0",
    "@types/react": "^18.2.0",
    "tailwindcss": "^3.4.0"
  }
}
```

### 3.2 Main Page

```tsx
// src/app/page.tsx
'use client';

import { CopilotKitProvider } from '@copilotkit/react-core/v2';
import { CopilotChat } from '@copilotkit/react-ui';
import { myCatalog } from '@/lib/a2ui/catalog';
import ChatPanel from '@/components/ChatPanel';

export default function Home() {
  return (
    <CopilotKitProvider 
      runtimeUrl="/api/copilotkit" 
      a2ui={{ catalog: myCatalog }}
    >
      <main className="min-h-screen bg-gray-100">
        <div className="max-w-4xl mx-auto p-4">
          <h1 className="text-3xl font-bold mb-6">AI Car Matchmaker</h1>
          <ChatPanel />
        </div>
      </main>
    </CopilotKitProvider>
  );
}
```

### 3.3 Chat Panel

```tsx
// src/components/ChatPanel.tsx
'use client';

import { useState } from 'react';
import { CopilotChat } from '@copilotkit/react-ui';
import { useCopilotReadable } from '@copilotkit/react-core';
import CarCard from './CarCard';
import InterviewProgress from './InterviewProgress';

export default function ChatPanel() {
  const [cars, setCars] = useState([]);
  const [progress, setProgress] = useState(0);

  useCopilotReadable({
    description: "Current interview progress",
    value: progress,
  });

  return (
    <div className="space-y-4">
      <InterviewProgress progress={progress} />
      
      {cars.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {cars.map((car) => (
            <CarCard key={car.id} car={car} />
          ))}
        </div>
      )}
      
      <div className="bg-white rounded-lg shadow-lg p-4">
        <CopilotChat />
      </div>
    </div>
  );
}
```

### 3.4 Car Card Component

```tsx
// src/components/CarCard.tsx
'use client';

interface CarCardProps {
  car: {
    id: string;
    make: string;
    model: string;
    year: number;
    price: { buy: number; rent_per_day: number };
    features: string[];
    image_url: string;
  };
}

export default function CarCard({ car }: CarCardProps) {
  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      <img 
        src={car.image_url} 
        alt={`${car.make} ${car.model}`}
        className="w-full h-48 object-cover"
      />
      <div className="p-4">
        <h3 className="text-xl font-bold">
          {car.year} {car.make} {car.model}
        </h3>
        <div className="mt-2 space-y-1">
          <p className="text-green-600 font-semibold">
            Buy: ${car.price.buy.toLocaleString()}
          </p>
          <p className="text-blue-600">
            Rent: ${car.price.rent_per_day}/day
          </p>
        </div>
        <div className="mt-3 flex flex-wrap gap-1">
          {car.features.slice(0, 3).map((feature) => (
            <span 
              key={feature}
              className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded"
            >
              {feature}
            </span>
          ))}
        </div>
        <button className="mt-4 w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700">
          Select Car
        </button>
      </div>
    </div>
  );
}
```

### 3.5 A2UI Catalog

```typescript
// src/lib/a2ui/catalog.ts
import { createCatalog } from '@copilotkit/a2ui-renderer';
import { z } from 'zod';

export const catalogDefinitions = {
  CarCard: {
    description: 'A car listing card with image, details, and action buttons.',
    props: z.object({
      make: z.string(),
      model: z.string(),
      year: z.number(),
      price: z.number(),
      imageUrl: z.string(),
    }),
  },
  BookingConfirmation: {
    description: 'A booking confirmation card with details.',
    props: z.object({
      bookingId: z.string(),
      carDetails: z.string(),
      dates: z.string(),
      total: z.number(),
    }),
  },
};

export const catalogRenderers = {
  CarCard: ({ props }) => (
    <div className="bg-white rounded-lg shadow-md p-4">
      <h3 className="text-lg font-bold">{props.year} {props.make} {props.model}</h3>
      <p className="text-green-600">${props.price.toLocaleString()}</p>
    </div>
  ),
  BookingConfirmation: ({ props }) => (
    <div className="bg-green-50 rounded-lg p-4">
      <h3 className="text-lg font-bold text-green-800">Booking Confirmed!</h3>
      <p>ID: {props.bookingId}</p>
      <p>Total: ${props.total}</p>
    </div>
  ),
};

export const myCatalog = createCatalog(catalogDefinitions, catalogRenderers, {
  catalogId: 'car-matchmaker',
  includeBasicCatalog: true,
});
```

---

## 4. Environment Variables

```bash
# .env.example
# LLM
GOOGLE_API_KEY=your_google_api_key
GROQ_API_KEY=your_groq_api_key

# Speech
DEEPGRAM_API_KEY=your_deepgram_api_key

# Email
SENDGRID_API_KEY=your_sendgrid_api_key
SENDGRID_FROM_EMAIL=noreply@car-matchmaker.ai

# SMS/Voice
TWILIO_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# Slack
SLACK_BOT_TOKEN=xoxb-your-slack-token
SLACK_CHANNEL=#car-bookings

# WhatsApp
WHATSAPP_TOKEN=your_whatsapp_token
WHATSAPP_PHONE_NUMBER=+1234567890

# App
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000
```

---

## 5. Running Locally

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

*Document Version: 1.0*
*Last Updated: August 2026*
