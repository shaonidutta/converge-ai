# Database Tables Detailed Explanation

**Date:** 2025-10-06  
**Purpose:** Comprehensive explanation of key database tables for frontend development

---

## 1. BOOKING_ITEMS Table

### Purpose
The `booking_items` table stores individual service items within a booking. A single booking can have multiple service items (e.g., AC Repair + Sofa Cleaning in one order).

### Key Columns Explained

#### `service_name` (VARCHAR 255)
**What it is:** The complete name of the service being booked.

**Value:** This is the **Rate Card name**, NOT just the subcategory name.

**Example:**
- Subcategory: "AC Repair"
- Rate Card names: 
  - "AC Repair - Basic" (₹500)
  - "AC Repair - Standard" (₹800)
  - "AC Repair - Premium" (₹1200)

**Frontend Perspective:**
```json
{
  "booking_item_id": 123,
  "service_name": "AC Repair - Premium",  // This is what user selected
  "subcategory_id": 15,                    // Links to "AC Repair" subcategory
  "rate_card_id": 45,                      // Links to specific pricing variant
  "price": 1200.00,
  "quantity": 1
}
```

**Why Rate Card name and not Subcategory?**
- A subcategory can have multiple pricing variants (Basic, Standard, Premium)
- Each variant has different features and prices
- `service_name` captures the exact variant the customer chose
- This appears on invoices, receipts, and order history

**Frontend Display:**
```
Order #ORD20251006123456
├── AC Repair - Premium (₹1,200)
├── Sofa Cleaning - Standard (₹800)
└── Kitchen Cleaning - Deep Clean (₹1,500)
Total: ₹3,500
```

### Complete Column List

| Column | Type | Description | Frontend Use |
|--------|------|-------------|--------------|
| `id` | INT | Primary key | Unique item identifier |
| `booking_id` | INT | Parent booking reference | Group items by order |
| `user_id` | INT | Customer who booked | Show customer details |
| `rate_card_id` | INT | Pricing variant selected | Get service details |
| `provider_id` | INT | Assigned service provider | Show provider info (can be NULL if not assigned yet) |
| `address_id` | INT | Service location | Show where service will be performed |
| `service_name` | VARCHAR | **Rate card name** | Display on UI, invoices, receipts |
| `quantity` | INT | Number of units | For services that can be multiple (e.g., 2 ACs) |
| `price` | DECIMAL | Unit price | Price per unit |
| `total_amount` | DECIMAL | price × quantity | Subtotal before discount |
| `discount_amount` | DECIMAL | Discount applied | Show savings |
| `final_amount` | DECIMAL | After discount | Actual amount for this item |
| `scheduled_date` | DATE | When service is scheduled | Calendar display |
| `scheduled_time_from` | TIME | Start time slot | "10:00 AM - 12:00 PM" |
| `scheduled_time_to` | TIME | End time slot | Time range display |
| `actual_start_time` | DATETIME | When provider actually started | Track actual service time |
| `actual_end_time` | DATETIME | When provider finished | Calculate duration |
| `cancel_by` | ENUM | Who cancelled (CUSTOMER/PROVIDER/EMPTY) | Show cancellation info |
| `cancel_reason` | TEXT | Why cancelled | Display reason |
| `payment_status` | ENUM | PAID/UNPAID/REFUND | Payment badge |
| `status` | ENUM | PENDING/ACCEPTED/IN_PROGRESS/COMPLETED/CANCELLED | Status badge |
| `created_at` | DATETIME | When item was created | Order timestamp |
| `updated_at` | DATETIME | Last update | Track changes |

---

## 2. CONVERSATIONS Table

### Purpose
Stores all chat messages between users and the AI assistant. Each message is a separate row, grouped by `session_id`.

### How to Identify Complete Conversation Sequentially

**Key Concept:** Use `session_id` + `created_at` for ordering

```sql
-- Get all messages for a session in chronological order
SELECT *
FROM conversations
WHERE session_id = 'SES20251006205348123456'
ORDER BY created_at ASC;
```

**Frontend Implementation:**
```javascript
// Group messages by session
const conversation = messages
  .filter(msg => msg.session_id === currentSessionId)
  .sort((a, b) => new Date(a.created_at) - new Date(b.created_at));

// Display in chat UI
conversation.forEach(msg => {
  if (msg.role === 'USER') {
    displayUserMessage(msg.message);
  } else {
    displayAssistantMessage(msg.message);
  }
});
```

### Complete Column Explanation

| Column | Type | Description | Frontend Use | Example Value |
|--------|------|-------------|--------------|---------------|
| `id` | INT | Primary key | Unique message ID | 1234 |
| `user_id` | INT | User who sent/received message | Link to user profile (NULL for anonymous) | 45 |
| `session_id` | VARCHAR(100) | **Conversation session identifier** | **Group all messages in one chat** | "SES20251006205348123456" |
| `role` | ENUM | USER or ASSISTANT | **Determine message alignment (left/right)** | "USER" or "ASSISTANT" |
| `message` | TEXT | **The actual message content** | **Display in chat bubble** | "I need to book AC repair" |
| `intent` | VARCHAR(50) | Detected user intent | Show intent badge (optional) | "booking" |
| `intent_confidence` | DECIMAL | AI confidence in intent (0-1) | Show confidence indicator | 0.95 |
| `agent_calls` | JSON | Which AI agents were invoked | Debug/analytics | {"agents": ["coordinator", "booking_agent"]} |
| `provenance` | JSON | Data sources used by AI | Show "Sources" section | {"sources": ["rate_cards", "bookings"]} |
| `grounding_score` | DECIMAL | How well AI used provided data (0-1) | Quality indicator | 0.92 |
| `faithfulness_score` | DECIMAL | How accurate AI response is (0-1) | Quality indicator | 0.88 |
| `relevancy_score` | DECIMAL | How relevant response is (0-1) | Quality indicator | 0.95 |
| `response_time_ms` | INT | AI response time in milliseconds | Show "typing" indicator | 1250 |
| `flagged_for_review` | BOOLEAN | Needs human review | Show warning icon | false |
| `review_reason` | VARCHAR(255) | Why flagged | Show reason | "Low confidence score" |
| `channel` | ENUM | WEB/MOBILE/WHATSAPP | Track conversation source | "WEB" |
| `created_at` | DATETIME | **Message timestamp** | **Sort messages chronologically** | "2025-10-06 20:53:48" |

### Frontend Chat UI Example

```javascript
// Conversation display
{
  session_id: "SES20251006205348123456",
  messages: [
    {
      id: 1,
      role: "USER",
      message: "I need AC repair service",
      created_at: "2025-10-06 10:00:00",
      channel: "WEB"
    },
    {
      id: 2,
      role: "ASSISTANT",
      message: "I can help you book AC repair. What's your pincode?",
      created_at: "2025-10-06 10:00:02",
      response_time_ms: 1200,
      grounding_score: 0.95,
      provenance: {"sources": ["rate_cards"]}
    },
    {
      id: 3,
      role: "USER",
      message: "400001",
      created_at: "2025-10-06 10:00:15"
    },
    {
      id: 4,
      role: "ASSISTANT",
      message: "Great! We have AC repair services available in 400001. Here are the options...",
      created_at: "2025-10-06 10:00:17",
      response_time_ms: 1500
    }
  ]
}
```

### Session Management

**New Session:** Generate new `session_id` when:
- User starts new chat
- User clicks "New Conversation"
- Session timeout (e.g., 30 minutes of inactivity)

**Continue Session:** Use existing `session_id` when:
- User sends another message in same chat
- User refreshes page (store session_id in localStorage)

---

## 3. PRIORITY_QUEUE Table

### Purpose
**Operations Review Queue** - Flags important conversations that need human (ops staff) attention.

**When Used:**
- AI detects complaint with negative sentiment
- User requests refund
- User wants to cancel booking
- Low confidence in AI response
- Escalation needed

### Use Case Flow

```
User Chat → AI Detects Issue → Add to Priority Queue → Ops Staff Reviews → Takes Action
```

**Example Scenario:**
1. User: "I'm very disappointed with the service quality. The provider was rude."
2. AI detects:
   - Intent: COMPLAINT
   - Sentiment: -0.8 (negative)
   - Confidence: 0.95
3. System automatically creates priority queue entry
4. Ops dashboard shows this in "High Priority" section
5. Ops staff reviews and takes action (call customer, assign manager, etc.)

### Complete Column Explanation

| Column | Type | Description | Frontend Use | Example |
|--------|------|-------------|--------------|---------|
| `id` | INT | Primary key | Queue item ID | 123 |
| `user_id` | INT | User who needs attention | Show user profile | 45 |
| `session_id` | VARCHAR(100) | Link to conversation | **Click to open full chat** | "SES20251006..." |
| `intent_type` | ENUM | COMPLAINT/REFUND/CANCELLATION/BOOKING | **Priority badge color** | "COMPLAINT" |
| `confidence_score` | DECIMAL | AI confidence (0-1) | Show confidence | 0.95 |
| `priority_score` | INT | Urgency score (0-100) | **Sort queue by priority** | 85 |
| `sentiment_score` | DECIMAL | User sentiment (-1 to +1) | Sentiment indicator | -0.75 (negative) |
| `message_snippet` | TEXT | Preview of issue | **Show in queue list** | "Very disappointed with..." |
| `is_reviewed` | BOOLEAN | Has ops staff seen this | **Filter reviewed/pending** | false |
| `reviewed_by` | INT | Which ops staff reviewed | Show reviewer name | 12 (ops staff ID) |
| `reviewed_at` | DATETIME | When reviewed | Show review time | "2025-10-06 11:30:00" |
| `action_taken` | TEXT | What ops did | Show resolution | "Escalated to manager" |
| `created_at` | DATETIME | When added to queue | **Sort by urgency** | "2025-10-06 10:00:00" |

### Frontend Ops Dashboard

```javascript
// Priority Queue Display
{
  high_priority: [
    {
      id: 123,
      user: "John Doe (+919876543210)",
      intent_type: "COMPLAINT",
      priority_score: 85,
      sentiment_score: -0.75,
      message_snippet: "Very disappointed with service quality...",
      created_at: "2 hours ago",
      is_reviewed: false,
      session_id: "SES20251006..."  // Click to open chat
    }
  ],
  medium_priority: [...],
  low_priority: [...]
}
```

### Priority Score Calculation

```
Base Priority by Intent:
- COMPLAINT: 80
- REFUND: 70
- CANCELLATION: 50
- BOOKING: 30

Adjustments:
+ Negative sentiment: +10 to +20
+ Low confidence: +5 to +10
+ VIP customer: +15
+ Repeat issue: +20

Final Score: 0-100 (higher = more urgent)
```

---

## 4. COMPLAINTS Table

### Purpose
Formal complaint tracking system with SLA (Service Level Agreement) management.

**Difference from Priority Queue:**
- **Priority Queue:** Real-time chat issues needing immediate attention
- **Complaints:** Formal complaints with ticket numbers, SLA tracking, resolution workflow

### When Used
- User files formal complaint
- Issue escalated from priority queue
- Service quality problems
- Billing disputes
- Provider behavior issues

### Complete Column Explanation

| Column | Type | Description | Frontend Use |
|--------|------|-------------|--------------|
| `id` | INT | Complaint ticket number | Display as "Ticket #123" |
| `booking_id` | INT | Related booking (optional) | Link to booking details |
| `user_id` | INT | Customer who complained | Show customer info |
| `session_id` | VARCHAR | Related chat session | Link to conversation |
| `complaint_type` | ENUM | SERVICE_QUALITY/PROVIDER_BEHAVIOR/BILLING/DELAY/CANCELLATION_ISSUE/REFUND_ISSUE/OTHER | Category badge |
| `subject` | VARCHAR(255) | Complaint title | Display as heading |
| `description` | TEXT | Detailed complaint | Show full description |
| `priority` | ENUM | LOW/MEDIUM/HIGH/CRITICAL | Priority badge |
| `status` | ENUM | OPEN/IN_PROGRESS/RESOLVED/CLOSED | Status badge |
| `assigned_to` | INT | Ops staff handling this | Show assignee |
| `assigned_at` | DATETIME | When assigned | Track assignment time |
| `resolution` | TEXT | How it was resolved | Show resolution |
| `resolved_by` | INT | Who resolved it | Show resolver |
| `resolved_at` | DATETIME | When resolved | Track resolution time |
| `response_due_at` | DATETIME | **SLA: First response deadline** | Show countdown timer |
| `resolution_due_at` | DATETIME | **SLA: Resolution deadline** | Show countdown timer |
| `created_at` | DATETIME | When complaint filed | Complaint age |
| `updated_at` | DATETIME | Last update | Track activity |

### SLA Tracking

```javascript
// Frontend SLA Display
{
  ticket_id: 123,
  status: "IN_PROGRESS",
  response_due_at: "2025-10-06 12:00:00",
  resolution_due_at: "2025-10-07 12:00:00",
  
  // Calculate time remaining
  response_sla: {
    due_in: "2 hours",
    status: "on_track",  // on_track / at_risk / breached
    color: "green"
  },
  resolution_sla: {
    due_in: "1 day 2 hours",
    status: "on_track",
    color: "green"
  }
}
```

---

## 5. COMPLAINT_UPDATES Table

### Purpose
Track all updates/comments on a complaint (like a ticket system).

### Complete Column Explanation

| Column | Type | Description | Frontend Use |
|--------|------|-------------|--------------|
| `id` | INT | Update ID | Unique identifier |
| `complaint_id` | INT | Parent complaint | Group updates by complaint |
| `user_id` | INT | Who added update | Show commenter (ops or customer) |
| `comment` | TEXT | Update message | Display in timeline |
| `is_internal` | BOOLEAN | Internal note (not visible to customer) | Hide from customer view |
| `attachments` | JSON | File attachments | Show download links |
| `created_at` | DATETIME | When added | Timeline order |

### Frontend Complaint Timeline

```javascript
// Complaint Detail Page
{
  complaint: {
    id: 123,
    subject: "Poor service quality",
    status: "IN_PROGRESS",
    created_at: "2025-10-06 10:00:00"
  },
  updates: [
    {
      id: 1,
      user: "John Doe (Customer)",
      comment: "The AC repair was incomplete. Still not cooling properly.",
      is_internal: false,
      created_at: "2025-10-06 10:00:00"
    },
    {
      id: 2,
      user: "Sarah (Ops Staff)",
      comment: "Contacted provider for clarification.",
      is_internal: false,
      created_at: "2025-10-06 10:30:00"
    },
    {
      id: 3,
      user: "Sarah (Ops Staff)",
      comment: "Provider has history of similar complaints. Consider blacklisting.",
      is_internal: true,  // Customer cannot see this
      created_at: "2025-10-06 10:35:00"
    },
    {
      id: 4,
      user: "Sarah (Ops Staff)",
      comment: "We've scheduled a re-service at no extra cost. Provider will visit tomorrow.",
      is_internal: false,
      created_at: "2025-10-06 11:00:00"
    }
  ]
}
```

---

## Summary for Frontend Development

### Key Relationships

```
BOOKING (Order)
  └── BOOKING_ITEMS (Individual services)
        ├── service_name = Rate Card name (e.g., "AC Repair - Premium")
        ├── Links to RATE_CARD (pricing variant)
        ├── Links to SUBCATEGORY (service type)
        └── Links to ADDRESS (service location)

CONVERSATION (Chat)
  ├── Grouped by session_id
  ├── Ordered by created_at
  └── role determines USER vs ASSISTANT messages

PRIORITY_QUEUE (Ops Review)
  ├── Links to CONVERSATION via session_id
  ├── Sorted by priority_score
  └── Filtered by is_reviewed

COMPLAINT (Formal Ticket)
  ├── Links to BOOKING (optional)
  ├── Links to CONVERSATION via session_id
  ├── Has SLA deadlines
  └── Has COMPLAINT_UPDATES (timeline)
```

### Frontend Query Examples

```sql
-- Get booking with all items
SELECT b.*, bi.service_name, bi.price, bi.quantity
FROM bookings b
JOIN booking_items bi ON b.id = bi.booking_id
WHERE b.id = 123;

-- Get conversation history
SELECT *
FROM conversations
WHERE session_id = 'SES20251006...'
ORDER BY created_at ASC;

-- Get pending priority queue items
SELECT *
FROM priority_queue
WHERE is_reviewed = false
ORDER BY priority_score DESC, created_at ASC;

-- Get complaint with updates
SELECT c.*, cu.comment, cu.created_at as update_time
FROM complaints c
LEFT JOIN complaint_updates cu ON c.id = cu.complaint_id
WHERE c.id = 123
ORDER BY cu.created_at ASC;
```

---

**End of Documentation**

