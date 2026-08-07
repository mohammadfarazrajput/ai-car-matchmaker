# SMS Messaging Plan (Twilio SMS)

## 1. Strategic Purpose & Placement
SMS acts as the immediate, lightweight, out-of-band notification engine. It delivers time-sensitive alerts, instant checkout links, and vehicle drop alerts directly to mobile devices.

```
+-----------------------+     +-------------------+     +-----------------------+
| Trigger Event         |     | Twilio SMS        |     | Customer Mobile Phone |
| (Price Drop / Rent)   | --> | Messaging Gateway | --> | (Immediate Engagement)|
+-----------------------+     +-------------------+     +-----------------------+
```

---

## 2. Communication Triggers & Message Templates

### A. Instant Booking & Reservation Link
* **Trigger:** User initiates reservation via A2UI but drops off before completing payment.
* **Delivery Window:** 5 minutes post-drop-off.
* **Template:**
  > *"Hi [Name], your reserved [BMW X5 / Vehicle] is holding for 15 minutes! Complete your booking here: https://amulate.app/c/[Session_ID]"*

### B. Price Drop & New Listing Alert
* **Trigger:** A saved preference matches a newly indexed listing or price decrease in SQLite dataset.
* **Template:**
  > *"Match Alert! A 2024 BMW i4 eDrive40 matching your criteria dropped by $1,200. View specs & lock price: https://amulate.app/v/[Vehicle_ID]"*

### C. Test Drive Confirmation
* **Trigger:** Completion of MCP Checkout App.
* **Template:**
  > *"Confirmed! Your test drive for the [Vehicle Name] is scheduled for [Date/Time] at [Dealership Name]. Reply CANCEL to reschedule."*

---

## 3. Implementation Verification Checklist
- [ ] Configured Twilio SMS client (`TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER`).
- [ ] Built SMS rate-limiting middleware to avoid spam threshold breaches.
- [ ] Verified incoming SMS webhook handler for opt-out / quick response tracking.
