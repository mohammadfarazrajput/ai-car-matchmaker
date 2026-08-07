# System Architecture & Data Flow Specification

## 1. Multistep Agent State Machine

```
         +-------------------------------------------------+
         |                  SESSION START                  |
         +------------------------+------------------------+
                                  |
                                  v
         +-------------------------------------------------+
         |               Phase 1: INTERVIEW                |
         |  - Solicit: Budget, Purchase vs. Rent, Dates,   |
         |    Car Types, Use Cases via A2UI Dynamic Form    |
         +------------------------+------------------------+
                                  |
                                  v
         +-------------------------------------------------+
         |               Phase 2: RESEARCH                 |
         |  - Query MCP / Mock Marketplace API             |
         |  - Filter 100+ vehicles across 10 categories     |
         +------------------------+------------------------+
                                  |
                                  v
         +-------------------------------------------------+
         |                Phase 3: RANKING                 |
         |  - Compute trade-off scores & match reasons     |
         |  - Render vehicle comparison cards in UI        |
         +------------------------+------------------------+
                                  |
                                  v
         +-------------------------------------------------+
         |               Phase 4: CHECKOUT                 |
         |  - Render MCP Form App (Driver details)         |
         |  - Render MCP Payment App (Mock safe checkout)  |
         +------------------------+------------------------+
                                  |
                                  v
         +-------------------------------------------------+
         |          Phase 5: MULTI-CHANNEL OUTREACH        |
         |  - SendGrid Email Dossier                       |
         |  - Twilio SMS Confirmation                      |
         |  - Slack Deal Channel Alert                     |
         |  - Schedule Twilio Voice Follow-up              |
         +-------------------------------------------------+
```

---

## 2. Mock Marketplace Schema (100+ Listings)

The local SQLite / JSON dataset provides 100+ listings spanning 10 categories (SUV, Sedan, EV, Luxury, Compact, Truck, Convertible, Van, Hybrid, Sports Car) with 10 brands per category.

```sql
CREATE TABLE listings (
    id TEXT PRIMARY KEY,
    make TEXT NOT NULL,
    model TEXT NOT NULL,
    year INTEGER NOT NULL,
    category TEXT NOT NULL, -- 'SUV', 'EV', 'Luxury', etc.
    listing_type TEXT NOT NULL, -- 'buy', 'rent', 'both'
    price_buy DECIMAL(10,2),
    price_rent_per_day DECIMAL(8,2),
    seating INTEGER NOT NULL,
    fuel_type TEXT NOT NULL, -- 'Gasoline', 'Electric', 'Hybrid', 'Plug-in Hybrid'
    range_or_mpg TEXT NOT NULL,
    safety_rating DECIMAL(3,1),
    features TEXT, -- JSON array of features
    image_url TEXT NOT NULL,
    is_available BOOLEAN DEFAULT 1
);
```

---

## 3. Generative UI (A2UI) Payload Protocol

The frontend receives streamed JSON payload frames conforming to the A2UI spec to dynamically render UI components in chat.

### Example A2UI Payload: Interview Dynamic Form
```json
{
  "protocol": "A2UI/1.0",
  "action": "RENDER_COMPONENT",
  "component": {
    "type": "InteractivePreferenceForm",
    "props": {
      "title": "Tell us about your driving needs",
      "fields": [
        { "id": "intent", "type": "select", "options": ["Buy", "Rent"] },
        { "id": "budget", "type": "range", "min": 5000, "max": 100000, "step": 2500 },
        { "id": "category", "type": "multi_chip", "options": ["SUV", "EV", "Luxury", "Sedan", "Sports"] },
        { "id": "target_date", "type": "date" }
      ]
    }
  }
}
```
