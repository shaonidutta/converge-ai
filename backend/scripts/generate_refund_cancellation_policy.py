"""
Generate Refund and Cancellation Policy
"""

import os
from datetime import datetime
from pathlib import Path

# Create directories
DOCS_DIR = Path(__file__).parent.parent / "data" / "policy_documents"
DOCS_DIR.mkdir(parents=True, exist_ok=True)

# Company information
COMPANY_INFO = {
    "name": "ConvergeAI Technologies Private Limited",
    "brand": "ConvergeAI",
    "address": "123 Tech Park, Sector 62, Noida, Uttar Pradesh 201301, India",
    "email": "support@convergeai.com",
    "phone": "+91-120-4567890",
    "website": "https://www.convergeai.com",
    "effective_date": "January 1, 2025",
    "last_updated": datetime.now().strftime("%B %d, %Y")
}


def generate_refund_cancellation_policy():
    """Generate comprehensive Refund and Cancellation Policy"""
    content = f"""
# REFUND AND CANCELLATION POLICY

**{COMPANY_INFO['brand']} - Service Marketplace Platform**

**Effective Date**: {COMPANY_INFO['effective_date']}  
**Last Updated**: {COMPANY_INFO['last_updated']}

---

## 1. INTRODUCTION

This Refund and Cancellation Policy outlines the terms and conditions for cancelling bookings and obtaining refunds on the ConvergeAI Platform. This policy is designed to be fair to both Customers and Service Providers while maintaining platform integrity.

### 1.1 Applicability

This policy applies to:
- All service bookings made through the Platform
- Both prepaid and postpaid services
- Cancellations initiated by Customers or Service Providers
- Refunds for service quality issues

### 1.2 Policy Updates

We reserve the right to modify this policy. Changes will be communicated through email and platform notifications.

---

## 2. CANCELLATION BY CUSTOMER

### 2.1 Standard Cancellation Policy

**Free Cancellation Window** (Full Refund):
- Cancellations made **more than 6 hours** before scheduled service time
- 100% refund of amount paid
- No cancellation charges
- Refund processed within 5-7 business days

**Partial Refund Window** (50% Refund):
- Cancellations made **3-6 hours** before scheduled service time
- 50% refund of service charge
- Platform fee non-refundable
- Refund processed within 5-7 business days

**No Refund Window**:
- Cancellations made **less than 3 hours** before scheduled service time
- No refund provided
- Full amount forfeited
- Service Provider compensation for blocked time slot

**Customer No-Show**:
- Customer not available at scheduled time
- Service Provider waited for 15 minutes
- No refund provided
- Full amount charged

### 2.2 Service-Specific Cancellation Policies

#### A. Home Cleaning Services
- Free cancellation: Up to 6 hours before
- Partial refund (50%): 3-6 hours before
- No refund: Less than 3 hours before

#### B. Appliance Repair Services
- Free cancellation: Up to 12 hours before
- Partial refund (50%): 6-12 hours before
- No refund: Less than 6 hours before
- Reason: Specialized technicians and parts arrangement

#### C. Beauty & Wellness Services
- Free cancellation: Up to 24 hours before
- Partial refund (50%): 12-24 hours before
- No refund: Less than 12 hours before
- Reason: Dedicated time slots and product preparation

#### D. Event Services (Photography, Catering)
- Free cancellation: Up to 7 days before
- Partial refund (50%): 3-7 days before
- Partial refund (25%): 1-3 days before
- No refund: Less than 24 hours before
- Reason: Advance booking and resource allocation

#### E. Tutoring & Education
- Free cancellation: Up to 4 hours before
- Partial refund (50%): 2-4 hours before
- No refund: Less than 2 hours before

#### F. Moving & Packing Services
- Free cancellation: Up to 48 hours before
- Partial refund (50%): 24-48 hours before
- No refund: Less than 24 hours before
- Reason: Vehicle and manpower arrangement

### 2.3 Emergency Cancellations (Full Refund)

Full refund provided for cancellations due to:

**Medical Emergencies**:
- Hospitalization of Customer or immediate family member
- Valid medical certificate required
- Must be submitted within 48 hours of cancellation

**Natural Disasters**:
- Floods, earthquakes, storms
- Government-declared emergencies
- Area-wide service disruptions

**Force Majeure Events**:
- Riots, civil unrest
- Government-imposed lockdowns
- Pandemic-related restrictions

**Service Provider Issues**:
- Service Provider cancellation
- Service Provider no-show
- Service Provider unprofessional behavior

### 2.4 How to Cancel

**Through Mobile App**:
1. Go to "My Bookings"
2. Select the booking
3. Click "Cancel Booking"
4. Select cancellation reason
5. Confirm cancellation

**Through Website**:
1. Login to your account
2. Navigate to "Bookings"
3. Select booking to cancel
4. Click "Cancel" and confirm

**Through Customer Support**:
- Call: {COMPANY_INFO['phone']}
- Email: support@convergeai.com
- Chat: Available in app

**Cancellation Confirmation**:
- Instant confirmation via SMS and email
- Cancellation ID provided
- Refund timeline communicated

---

## 3. CANCELLATION BY SERVICE PROVIDER

### 3.1 Service Provider Cancellation

If a Service Provider cancels:

**Customer Rights**:
- Full refund (100%)
- Instant refund to original payment method
- Option to reschedule with same or different provider
- Compensation credit (₹100-500 based on inconvenience)

**Service Provider Penalties**:
- First cancellation: Warning
- Second cancellation: ₹500 penalty
- Third cancellation: ₹1000 penalty + 7-day suspension
- Repeated cancellations: Permanent account suspension

**Exceptions** (No Penalty):
- Medical emergencies (with proof)
- Vehicle breakdown (with proof)
- Natural disasters
- Family emergencies (with proof)

### 3.2 Service Provider No-Show

If Service Provider doesn't arrive:

**Customer Actions**:
- Wait for 15 minutes beyond scheduled time
- Contact Service Provider via app
- Report no-show through app

**Customer Compensation**:
- Full refund (100%)
- Additional compensation: ₹200-1000
- Priority booking for rescheduled service
- Waived service fee for next booking

**Service Provider Consequences**:
- First no-show: ₹1000 penalty + warning
- Second no-show: ₹2000 penalty + 15-day suspension
- Third no-show: Permanent account termination

---

## 4. REFUND PROCESS

### 4.1 Refund Timeline

**Wallet Refunds**:
- Instant credit to ConvergeAI Wallet
- Available for immediate use
- No processing time

**Original Payment Method**:
- Credit/Debit Card: 5-7 business days
- Net Banking: 5-7 business days
- UPI: 3-5 business days
- Digital Wallets: 3-5 business days

**Bank Processing Time**:
- Additional 2-3 days for bank processing
- Varies by bank and payment method
- Weekends and holidays may cause delays

### 4.2 Refund Methods

Refunds are processed to:
- Original payment method (default)
- ConvergeAI Wallet (if requested)
- Bank account (for cash payments)

### 4.3 Refund Calculation

**Full Refund**:
- Service charge: 100%
- Platform fee: 100%
- Taxes: 100%
- Total amount paid: 100%

**Partial Refund (50%)**:
- Service charge: 50%
- Platform fee: 0% (non-refundable)
- Taxes: Proportional to refunded amount

**Example**:
- Service Charge: ₹1000
- Platform Fee: ₹150
- GST (18%): ₹207
- Total Paid: ₹1357

*50% Refund*:
- Service Charge Refund: ₹500
- Platform Fee Refund: ₹0
- GST Refund: ₹90
- Total Refund: ₹590

### 4.4 Refund Tracking

Track refund status:
- In-app: "My Bookings" > "Refunds"
- Email notifications at each stage
- SMS updates
- Customer support: support@convergeai.com

**Refund Stages**:
1. Cancellation Confirmed
2. Refund Initiated
3. Refund Processed
4. Refund Credited (by bank)

---

## 5. SERVICE QUALITY ISSUES

### 5.1 Partial Service Completion

If service is partially completed:

**Assessment**:
- Customer reports incomplete service
- Service Provider provides explanation
- Platform reviews evidence (photos, chat logs)

**Refund Calculation**:
- Based on percentage of work completed
- Verified through inspection (if needed)
- Proportional refund issued

**Example**:
- Booked: Full home deep cleaning (₹2000)
- Completed: Only 2 out of 4 rooms
- Refund: 50% (₹1000)

### 5.2 Poor Service Quality

If service quality is unsatisfactory:

**Complaint Process**:
1. Report issue within 24 hours of service
2. Provide details and evidence (photos/videos)
3. Platform investigates (1-3 business days)
4. Resolution provided based on findings

**Possible Resolutions**:
- Free re-service (preferred option)
- Partial refund (25-75% based on severity)
- Full refund (for severe quality issues)
- Compensation credit for inconvenience

**Quality Issue Categories**:

**Minor Issues** (25% Refund):
- Slight delays (15-30 minutes)
- Minor quality concerns
- Incomplete cleaning of small areas

**Moderate Issues** (50% Refund):
- Significant delays (30-60 minutes)
- Noticeable quality problems
- Incomplete work in major areas

**Major Issues** (75-100% Refund):
- Severe delays (>60 minutes)
- Unacceptable quality
- Damage to property
- Unprofessional behavior

### 5.3 Service Not as Described

If service differs from description:

**Examples**:
- Different service provided
- Missing inclusions
- Incorrect pricing applied
- Unauthorized additional charges

**Resolution**:
- Full refund if service not provided as described
- Compensation for inconvenience
- Corrective action against Service Provider

---

## 6. RESCHEDULING

### 6.1 Rescheduling Policy

**Free Rescheduling**:
- First reschedule: Free (if done 6+ hours before)
- Must be within 30 days of original booking
- Subject to Service Provider availability

**Paid Rescheduling**:
- Second reschedule: ₹50 fee
- Third reschedule: ₹100 fee
- Less than 6 hours before: ₹200 fee

**How to Reschedule**:
1. Go to "My Bookings"
2. Select booking
3. Click "Reschedule"
4. Choose new date/time
5. Confirm reschedule

### 6.2 Rescheduling by Service Provider

If Service Provider requests reschedule:

**Customer Options**:
- Accept new date/time (no charges)
- Decline and get full refund
- Request different Service Provider

**Service Provider Penalties**:
- First reschedule: Warning
- Repeated rescheduling: Penalties apply

---

## 7. SPECIAL CIRCUMSTANCES

### 7.1 Weather-Related Cancellations

**Severe Weather Conditions**:
- Heavy rain, storms, floods
- Government weather warnings
- Unsafe travel conditions

**Policy**:
- Full refund or free rescheduling
- No penalties for either party
- Platform monitors weather conditions

### 7.2 COVID-19 and Health Concerns

**Customer Symptoms**:
- Customer or family member has symptoms
- Recent COVID-19 exposure
- Quarantine requirements

**Policy**:
- Full refund with medical certificate
- Free rescheduling option
- No questions asked cancellation

**Service Provider Symptoms**:
- Service Provider has symptoms
- Recent exposure
- Quarantine requirements

**Policy**:
- Customer gets full refund
- Free rescheduling with different provider
- No penalty for Service Provider (with proof)

### 7.3 Address Issues

**Incorrect Address**:
- Customer provided wrong address
- Service Provider unable to locate
- Customer not reachable

**Policy**:
- No refund if Customer's fault
- One-time address correction allowed
- Additional travel charges may apply

**Inaccessible Location**:
- Gated community access denied
- Building restrictions
- Security issues

**Policy**:
- Full refund if genuinely inaccessible
- Customer must resolve access issues
- Rescheduling option available

---

## 8. REFUND EXCEPTIONS

### 8.1 Non-Refundable Scenarios

No refund provided for:
- Services already completed
- Customer no-show
- Late cancellations (as per policy)
- Promotional/discounted bookings (specific terms apply)
- Gift card purchases
- Wallet top-ups

### 8.2 Promotional Bookings

Bookings made with promotional codes:
- Standard cancellation policy applies
- Promotional discount may be forfeited
- Refund calculated on amount paid
- Promotional code may not be reusable

### 8.3 Subscription/Package Bookings

For subscription or package bookings:
- Pro-rated refund for unused services
- Cancellation fee may apply
- Terms specified in package details
- Minimum usage period may apply

---

## 9. DISPUTE RESOLUTION

### 9.1 Refund Disputes

If you disagree with refund decision:

**Step 1: Contact Support**
- Email: refunds@convergeai.com
- Phone: {COMPANY_INFO['phone']}
- Provide booking ID and details

**Step 2: Escalation**
- Request escalation to senior team
- Provide additional evidence
- Response within 3-5 business days

**Step 3: Final Review**
- Management review
- Final decision communicated
- Decision is binding

### 9.2 Chargeback Policy

**Before Filing Chargeback**:
- Contact our support team first
- Allow 7-10 days for resolution
- Provide all relevant information

**Chargeback Consequences**:
- Account may be suspended during investigation
- If chargeback is unjustified:
  - Account permanently suspended
  - Legal action may be taken
  - Chargeback fees recovered

---

## 10. CONTACT INFORMATION

For cancellation and refund queries:

**Customer Support**  
Email: support@convergeai.com  
Phone: {COMPANY_INFO['phone']}  
Hours: 24/7

**Refund Queries**  
Email: refunds@convergeai.com  
Response Time: Within 24 hours

**Escalations**  
Email: escalations@convergeai.com  
Phone: {COMPANY_INFO['phone']} (Press 2)

---

**This policy is subject to change. Please review before each booking.**

---

*Document Version: 1.0*  
*Effective Date: {COMPANY_INFO['effective_date']}*  
*Last Updated: {COMPANY_INFO['last_updated']}*
"""
    
    filepath = DOCS_DIR / "03_Refund_and_Cancellation_Policy.md"
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content.strip())
    
    print(f"✅ Generated: {filepath}")
    return filepath


if __name__ == "__main__":
    print("=" * 80)
    print("GENERATING REFUND AND CANCELLATION POLICY")
    print("=" * 80)
    print()
    
    generate_refund_cancellation_policy()
    
    print()
    print("=" * 80)
    print("DOCUMENT GENERATION COMPLETE")
    print(f"Documents saved to: {DOCS_DIR}")
    print("=" * 80)

