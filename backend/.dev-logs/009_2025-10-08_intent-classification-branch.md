# Intent Classification Branch Setup

**Date:** 2025-10-08  
**Branch:** feature/intent-classification  
**Status:** ✅ **READY FOR DEVELOPMENT**

---

## 🎯 Branch Purpose

This branch is dedicated to implementing the **Intent Classification System** for ConvergeAI's chatbot. This will enable the system to understand user queries and route them to appropriate specialized agents.

---

## 📋 What Was Done

### 1. ✅ **Committed Chat API**
- Committed chat API implementation to `feature/embedding-vector-store-setup`
- Pushed to remote repository

### 2. ✅ **Merged to Master**
- Pulled latest changes from master
- Merged `feature/embedding-vector-store-setup` into `master`
- Pushed updated master to remote

### 3. ✅ **Created New Branch**
- Created `feature/intent-classification` branch from master
- Pushed to remote and set up tracking

---

## 🎯 Intent Classification Implementation Plan

### **Comprehensive Intent List (120 Intents)**

Based on our earlier discussion, we need to implement classification for these intent categories:

#### **1. Booking & Scheduling (10 intents)**
- book_service
- reschedule_booking
- cancel_booking
- modify_booking
- check_booking_status
- emergency_service
- recurring_service
- multi_service_booking
- technician_preference
- add_service_to_booking

#### **2. Pricing & Availability (10 intents)**
- price_inquiry
- check_availability
- view_booking_history
- check_service_area
- get_quote
- compare_pricing
- bulk_booking_discount
- seasonal_offers
- transaction_history
- payment_history

#### **3. Service Information (11 intents)**
- service_info
- service_recommendations
- compare_services
- service_process
- service_duration
- what_included
- preparation_required
- technician_qualifications
- service_benefits
- faq
- how_to_use_platform

#### **4. Policies & Terms (10 intents)**
- policy_info
- cancellation_policy
- refund_policy
- warranty_info
- terms_conditions
- privacy_policy
- service_guarantee
- rescheduling_policy
- late_cancellation_fee
- no_show_policy

#### **5. Complaints & Issues (10 intents)**
- complaint_issue
- service_quality_issue
- technician_behavior
- damage_claim
- incomplete_service
- wrong_service
- technician_late
- technician_no_show
- report_problem
- escalate_complaint

#### **6. Payment & Billing (14 intents)**
- payment_inquiry
- payment_issue
- payment_pending
- double_charged
- wrong_amount_charged
- payment_methods
- update_payment_method
- save_payment_method
- payment_receipt
- invoice_request
- payment_confirmation
- partial_payment
- advance_payment
- cod_option

#### **7. Refunds & Credits (11 intents)**
- refund_request
- refund_status
- refund_timeline
- partial_refund
- refund_to_wallet
- cancellation_refund
- wallet_balance
- wallet_credit
- use_wallet
- credit_note
- compensation_request

#### **8. Feedback & Ratings (7 intents)**
- provide_feedback
- rate_service
- write_review
- update_rating
- view_my_reviews
- compliment_technician
- service_satisfaction

#### **9. Account Management (12 intents)**
- update_profile
- change_phone
- change_email
- manage_addresses
- set_default_address
- delete_account
- update_preferences
- notification_settings
- language_preference
- loyalty_rewards
- referral_program
- redeem_points

#### **10. Tracking & Real-time (6 intents)**
- track_technician
- technician_eta
- contact_technician
- technician_details
- service_progress
- notify_arrival

#### **11. Coupons & Offers (7 intents)**
- apply_coupon
- available_coupons
- coupon_validity
- first_time_discount
- referral_discount
- seasonal_offers
- combo_offers

#### **12. Conversational (6 intents)**
- greeting
- farewell
- acknowledgment
- appreciation
- small_talk
- help_general

#### **13. Special Cases (6 intents)**
- unclear_intent
- out_of_scope
- multiple_intents
- need_clarification
- human_support
- callback_request

---

## 🛠️ Implementation Approach

### **Phase 1: Hybrid Intent Classification (Recommended)**

```
User Query
    ↓
┌─────────────────────────────────────┐
│ 1. Quick Pattern Matching           │
│    (Regex/Keywords - Fast & Cheap)  │
└─────────────────┬───────────────────┘
                  │
                  ├─→ High Confidence (>0.9) → Return Intent
                  │
                  ↓
┌─────────────────────────────────────┐
│ 2. LLM Classification (Gemini)      │
│    (For ambiguous cases)            │
└─────────────────┬───────────────────┘
                  │
                  ├─→ Confidence >0.7 → Return Intent
                  │
                  ↓
┌─────────────────────────────────────┐
│ 3. Fallback to Coordinator Agent    │
│    (Ask clarifying questions)       │
└─────────────────────────────────────┘
```

### **Components to Build:**

1. **Intent Classifier** (`backend/src/nlp/intent/classifier.py`)
   - Pattern-based classification (fast path)
   - LLM-based classification (fallback)
   - Confidence scoring
   - Entity extraction

2. **Intent Patterns** (`backend/src/nlp/intent/patterns.py`)
   - Keyword patterns for each intent
   - Regex patterns
   - Common phrases

3. **Intent Service** (`backend/src/services/intent_service.py`)
   - Classify intent from user message
   - Extract entities
   - Return intent with confidence score

4. **Integration with ChatService**
   - Replace placeholder in `_get_ai_response()`
   - Call IntentService
   - Store intent and confidence in database

5. **Agent Router** (`backend/src/agents/router.py`)
   - Route to appropriate agent based on intent
   - Handle multi-intent scenarios
   - Fallback handling

---

## 📊 Agent Mapping

| Intent Category | Agent | Status |
|----------------|-------|--------|
| Booking & Scheduling | BookingAgent | ✅ Exists |
| Pricing & Availability | SQLAgent | ✅ Exists |
| Service Information | RAGAgent | ⏳ To Build |
| Policies & Terms | PolicyAgent | ⏳ To Build |
| Complaints & Issues | ComplaintAgent | ✅ Exists |
| Payment & Billing | PaymentAgent | ⏳ To Build |
| Refunds & Credits | RefundAgent | ⏳ To Build |
| Feedback & Ratings | FeedbackAgent | ⏳ To Build |
| Account Management | AccountAgent | ⏳ To Build |
| Tracking & Real-time | TrackingAgent | ⏳ To Build |
| Coupons & Offers | PromotionAgent | ⏳ To Build |
| Conversational | Coordinator | ✅ Exists |
| Special Cases | Coordinator | ✅ Exists |

---

## 🚀 Next Steps

### **Immediate Tasks:**

1. **Create Intent Classifier**
   - Implement pattern-based classification
   - Integrate Gemini for ambiguous cases
   - Add confidence scoring

2. **Define Intent Patterns**
   - Create keyword/regex patterns for all 120 intents
   - Test with sample queries

3. **Build Intent Service**
   - Service layer for intent classification
   - Entity extraction
   - Caching for performance

4. **Integrate with Chat API**
   - Update `ChatService._get_ai_response()`
   - Store intent and confidence in database
   - Add intent to response

5. **Create Agent Router**
   - Route to appropriate agent based on intent
   - Handle edge cases
   - Fallback logic

6. **Testing**
   - Unit tests for intent classifier
   - Integration tests with chat API
   - Test all 120 intents

---

## 📝 Files to Create

```
backend/src/nlp/intent/
├── __init__.py
├── classifier.py          # Main intent classifier
├── patterns.py            # Intent patterns and keywords
├── entities.py            # Entity extraction
└── config.py              # Intent configuration

backend/src/services/
└── intent_service.py      # Intent service layer

backend/src/agents/
└── router.py              # Agent routing logic

backend/tests/unit/nlp/
└── test_intent_classifier.py
```

---

## 🎯 Success Criteria

- ✅ Classify 120 intents with >85% accuracy
- ✅ Response time <500ms for pattern matching
- ✅ Response time <2s for LLM classification
- ✅ Confidence scores for all classifications
- ✅ Entity extraction working
- ✅ Integration with chat API complete
- ✅ All tests passing

---

## 📚 Resources

- Intent list: See comprehensive list above
- Chat API: `backend/src/api/v1/routes/chat.py`
- Chat Service: `backend/src/services/chat_service.py`
- Conversation Model: `backend/src/core/models/conversation.py`

---

**Status:** ✅ Branch ready for intent classification implementation!

