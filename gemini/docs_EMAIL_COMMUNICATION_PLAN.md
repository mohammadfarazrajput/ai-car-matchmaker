# Email Communication Plan (SendGrid)

## 1. Strategic Purpose & Placement
Email provides rich, asynchronous, visual communications. It delivers comprehensive vehicle comparison dossiers, finance calculation breakdowns, and official booking receipts.

```
+-----------------------+     +-------------------+     +-----------------------+
| Multistep Agent       |     | SendGrid API      |     | Customer Inbox        |
| (Match Completed)     | --> | Dynamic Templates | --> | (Rich PDF/HTML Report)|
+-----------------------+     +-------------------+     +-----------------------+
```

---

## 2. Core Email Workflows

### A. Personalized Vehicle Match Dossier
* **Trigger:** Agent completes Phase 3 (RANKING) during user session.
* **Content:** High-resolution dynamic HTML email featuring top 3 matched vehicles, trade-off comparisons, total cost of ownership estimates, and attached PDF summary dossier.

### B. Reservation & Safe Checkout Receipt
* **Trigger:** Completion of Phase 4 (MCP Payment App execution).
* **Content:** Official booking receipt detailing transaction ID, vehicle VIN/ID, deposit paid, dealership contact, and next steps.

---

## 3. Dynamic HTML Email Template Specification

```html
<!DOCTYPE html>
<html>
<head>
  <style>
    body { font-family: 'Helvetica Neue', Arial, sans-serif; background-color: #f4f6f8; color: #1a1a1a; margin: 0; padding: 20px; }
    .card { background: #ffffff; border-radius: 8px; padding: 24px; max-width: 600px; margin: 0 auto; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
    .header { border-bottom: 2px solid #0066b1; padding-bottom: 12px; margin-bottom: 20px; }
    .title { color: #0066b1; font-size: 20px; font-weight: bold; }
    .vehicle-row { display: table; width: 100%; margin-bottom: 16px; border-bottom: 1px solid #e0e0e0; padding-bottom: 12px; }
    .button { background-color: #0066b1; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; display: inline-block; font-weight: bold; }
  </style>
</head>
<body>
  <div class="card">
    <div class="header">
      <h2>Amulate AI Matchmaker Summary</h2>
    </div>
    <p>Hello <strong>{{ user_name }}</strong>,</p>
    <p>Based on your criteria ({{ category_preference }} | {{ budget_range }}), here is your curated selection:</p>
    
    {{#each top_matches}}
    <div class="vehicle-row">
      <h3>{{ this.year }} {{ this.make }} {{ this.model }}</h3>
      <p><strong>Match Score:</strong> {{ this.match_score }}%</p>
      <p><strong>Reasoning:</strong> {{ this.reasoning }}</p>
      <p><strong>Price:</strong> {{ this.price_formatted }}</p>
    </div>
    {{/each}}
    
    <div style="text-align: center; margin-top: 24px;">
      <a href="{{ checkout_url }}" class="button">Complete Reservation</a>
    </div>
  </div>
</body>
</html>
```

---

## 4. Implementation Verification Checklist
- [ ] SendGrid API key configured and verified with Sender Authentication.
- [ ] Dynamic template mappings defined for Dossier and Receipt events.
- [ ] Verified WeasyPrint PDF generation for attached vehicle dossier reports.
