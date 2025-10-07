"""
Generate comprehensive policy documents for ConvergeAI marketplace
Creates detailed legal documents covering all aspects of the platform
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
    "gstin": "09AABCC1234F1Z5",
    "cin": "U72900DL2024PTC123456",
    "effective_date": "January 1, 2025",
    "last_updated": datetime.now().strftime("%B %d, %Y")
}


def generate_terms_and_conditions():
    """Generate comprehensive Terms and Conditions"""
    content = f"""
# TERMS AND CONDITIONS

**{COMPANY_INFO['brand']} - Service Marketplace Platform**

**Effective Date**: {COMPANY_INFO['effective_date']}  
**Last Updated**: {COMPANY_INFO['last_updated']}

---

## 1. INTRODUCTION AND ACCEPTANCE OF TERMS

### 1.1 About ConvergeAI

{COMPANY_INFO['name']} ("Company", "we", "us", or "our"), operating under the brand name "{COMPANY_INFO['brand']}", provides an online marketplace platform connecting customers seeking home and professional services with independent service providers. Our platform facilitates service discovery, booking, payment processing, and customer support.

### 1.2 Acceptance of Terms

By accessing, browsing, or using the ConvergeAI platform (including our website, mobile applications, and any related services, collectively referred to as the "Platform"), you ("User", "you", or "your") acknowledge that you have read, understood, and agree to be bound by these Terms and Conditions ("Terms"), along with our Privacy Policy, Refund Policy, and any other policies referenced herein.

### 1.3 Eligibility

To use our Platform, you must:
- Be at least 18 years of age
- Have the legal capacity to enter into binding contracts
- Not be prohibited from using the Platform under applicable laws
- Provide accurate and complete registration information
- Maintain the security of your account credentials

### 1.4 Modifications to Terms

We reserve the right to modify these Terms at any time. Material changes will be notified through:
- Email notification to registered users
- Prominent notice on the Platform
- In-app notifications

Continued use of the Platform after such modifications constitutes acceptance of the revised Terms.

---

## 2. DEFINITIONS

For the purposes of these Terms:

**"Customer"** means any individual or entity using the Platform to book services.

**"Service Provider"** or **"Provider"** means any independent contractor registered on the Platform to offer services.

**"Service"** means any home service, professional service, or related offering available through the Platform.

**"Booking"** means a confirmed service request placed by a Customer through the Platform.

**"Service Fee"** means the fee charged by the Platform for facilitating the transaction.

**"Service Charge"** means the amount payable to the Service Provider for performing the service.

**"Total Amount"** means the sum of Service Charge, Service Fee, applicable taxes, and any other charges.

---

## 3. PLATFORM SERVICES

### 3.1 Nature of Services

ConvergeAI operates as an intermediary platform that:
- Connects Customers with Service Providers
- Facilitates service discovery and booking
- Processes payments on behalf of Service Providers
- Provides customer support and dispute resolution
- Maintains quality standards through ratings and reviews

### 3.2 Platform Role

**IMPORTANT**: ConvergeAI is a technology platform and marketplace facilitator. We:
- Do NOT employ Service Providers
- Do NOT provide services directly
- Do NOT guarantee service quality or outcomes
- Act solely as an intermediary between Customers and Service Providers

Service Providers are independent contractors responsible for their own services, equipment, insurance, and compliance with applicable laws.

### 3.3 Service Categories

The Platform offers services across multiple categories including but not limited to:
- Home Cleaning (Deep Cleaning, Regular Cleaning, Kitchen, Bathroom, Sofa)
- Appliance Repair (AC, Refrigerator, Washing Machine, Microwave, TV)
- Plumbing (Installation, Repair, Maintenance)
- Electrical Services (Wiring, Fixture Installation, Repair)
- Carpentry (Furniture Assembly, Repair, Custom Work)
- Painting (Interior, Exterior, Touch-up)
- Pest Control (Termite, Cockroach, Rodent, Bed Bug)
- Beauty & Wellness (Salon at Home, Spa, Massage)
- Tutoring & Education (Academic, Music, Language, Skill Development)
- Event Services (Photography, Catering, Decoration)
- Moving & Packing
- And other services as added from time to time

---

## 4. USER ACCOUNTS

### 4.1 Registration

To use certain features of the Platform, you must create an account by providing:
- Valid mobile number (mandatory)
- Email address (recommended)
- Full name
- Service address (for Customers)
- Additional information as required

### 4.2 Account Security

You are responsible for:
- Maintaining the confidentiality of your account credentials
- All activities that occur under your account
- Notifying us immediately of any unauthorized access
- Using strong passwords and enabling two-factor authentication

### 4.3 Account Verification

We may require verification of:
- Mobile number (via OTP)
- Email address (via verification link)
- Identity documents (for Service Providers)
- Address proof (for Service Providers)
- Professional certifications (for specialized services)

### 4.4 Account Suspension and Termination

We reserve the right to suspend or terminate accounts that:
- Violate these Terms
- Engage in fraudulent activities
- Provide false information
- Abuse the Platform or other users
- Fail to pay outstanding amounts
- Receive multiple negative reviews or complaints

---

## 5. BOOKING PROCESS

### 5.1 Service Discovery

Customers can discover services through:
- Category browsing
- Search functionality
- AI-powered recommendations
- Featured services
- Location-based suggestions

### 5.2 Service Selection

When selecting a service, Customers can view:
- Service description and inclusions
- Pricing and package options
- Service Provider ratings and reviews
- Estimated duration
- Availability
- Terms and conditions specific to the service

### 5.3 Booking Confirmation

A booking is confirmed when:
- Customer selects service, date, time, and address
- Customer reviews and accepts the total amount
- Payment is successfully processed or payment method is confirmed
- Service Provider accepts the booking (if applicable)
- Customer receives booking confirmation via SMS/email

### 5.4 Booking Modifications

Customers may modify bookings subject to:
- Modification request made at least 6 hours before scheduled time
- Service Provider availability for new date/time
- No additional charges for first modification
- Subsequent modifications may incur charges

### 5.5 Service Provider Assignment

- Service Providers are assigned based on availability, location, ratings, and specialization
- Customers may request specific Service Providers (subject to availability)
- We reserve the right to reassign Service Providers due to unavailability or other factors

---

## 6. PRICING AND PAYMENTS

### 6.1 Pricing Structure

Prices displayed on the Platform include:
- Base service charge
- Platform service fee
- Applicable taxes (GST)
- Any additional charges (materials, travel, etc.)

### 6.2 Price Variations

Prices may vary based on:
- Service location (pincode)
- Service complexity
- Time of service (peak hours, weekends, holidays)
- Seasonal demand
- Special requirements

### 6.3 Payment Methods

Accepted payment methods include:
- Credit/Debit Cards (Visa, Mastercard, RuPay, Amex)
- Net Banking
- UPI (Google Pay, PhonePe, Paytm, etc.)
- Digital Wallets (Paytm, Mobikwik, etc.)
- Cash on Delivery (for select services)
- ConvergeAI Wallet

### 6.4 Payment Processing

- Payments are processed through secure, PCI-DSS compliant payment gateways
- Payment information is encrypted and not stored on our servers
- Payment confirmation is sent via SMS/email
- Invoices are generated and available in user account

### 6.5 Payment Timing

- **Prepaid Services**: Full payment required at booking
- **Postpaid Services**: Payment after service completion
- **Partial Payment**: Advance payment with balance due after service

### 6.6 Service Fee

ConvergeAI charges a service fee (typically 10-20% of service charge) for:
- Platform maintenance and development
- Customer support
- Payment processing
- Quality assurance
- Marketing and promotions

### 6.7 Additional Charges

Additional charges may apply for:
- Materials and consumables used
- Extra work beyond scope
- Travel beyond standard radius
- Urgent or same-day bookings
- Specialized equipment or tools

Customers will be informed of additional charges before they are applied.

---

## 7. CANCELLATION AND REFUNDS

### 7.1 Cancellation by Customer

**Free Cancellation Window**: 
- Cancellations made more than 6 hours before scheduled time: Full refund
- Cancellations made 3-6 hours before: 50% refund
- Cancellations made less than 3 hours before: No refund
- No-show by Customer: No refund

**Exceptions**:
- Medical emergencies (with valid documentation): Full refund
- Natural disasters or force majeure: Full refund
- Service Provider cancellation: Full refund

### 7.2 Cancellation by Service Provider

If a Service Provider cancels:
- Customer receives full refund
- Service Provider may face penalties
- We will attempt to assign alternate Service Provider
- Customer may choose to reschedule or cancel

### 7.3 Refund Processing

- Refunds are processed within 5-7 business days
- Refunds are credited to original payment method
- Wallet refunds are instant
- Refund status can be tracked in user account

### 7.4 Partial Refunds

Partial refunds may be issued for:
- Incomplete services
- Service quality issues
- Delayed service completion
- Scope reduction

Amount determined based on work completed and issue severity.

---

## 8. SERVICE QUALITY AND STANDARDS

### 8.1 Quality Commitment

We strive to maintain high service quality through:
- Service Provider verification and background checks
- Training and certification programs
- Regular quality audits
- Customer feedback and ratings
- Mystery shopping programs

### 8.2 Service Standards

Service Providers are expected to:
- Arrive on time (within 15-minute window)
- Carry necessary tools and equipment
- Wear proper identification
- Maintain professional conduct
- Complete work as per specifications
- Clean up after service completion
- Provide service warranty (if applicable)

### 8.3 Customer Responsibilities

Customers must:
- Provide accurate service address and contact information
- Be present or arrange for someone to be present
- Provide access to service area
- Inform of any special requirements or hazards
- Provide necessary utilities (water, electricity)
- Secure valuables and pets

### 8.4 Service Warranty

- Standard warranty: 7-30 days (varies by service)
- Warranty covers workmanship defects
- Warranty does not cover misuse or normal wear
- Warranty claims must be reported within warranty period
- Free re-service provided for valid warranty claims

---

## 9. RATINGS AND REVIEWS

### 9.1 Review System

Customers can rate and review:
- Service quality (1-5 stars)
- Service Provider professionalism
- Timeliness
- Value for money
- Overall experience

### 9.2 Review Guidelines

Reviews must:
- Be based on actual service experience
- Be honest and factual
- Not contain offensive language
- Not include personal information
- Not be incentivized or fake

### 9.3 Review Moderation

We reserve the right to:
- Remove reviews violating guidelines
- Verify authenticity of reviews
- Take action against fake reviews
- Respond to reviews on behalf of Service Providers

### 9.4 Impact on Service Providers

- Low ratings may result in reduced visibility
- Consistently poor ratings may lead to suspension
- High ratings earn featured placement
- Reviews influence customer booking decisions

---

## 10. COMPLAINTS AND DISPUTE RESOLUTION

### 10.1 Complaint Process

Customers can file complaints for:
- Service quality issues
- Service Provider behavior
- Billing disputes
- Delayed or incomplete service
- Safety concerns

### 10.2 Complaint Channels

- In-app complaint form
- Email: complaints@convergeai.com
- Phone: +91-120-4567890
- Customer support chat

### 10.3 Complaint Resolution

- Complaints acknowledged within 24 hours
- Investigation completed within 3-5 business days
- Resolution provided based on findings
- Escalation to senior team if unresolved

### 10.4 Dispute Resolution

For unresolved disputes:
- Mediation through Platform
- Arbitration as per Indian Arbitration and Conciliation Act, 1996
- Jurisdiction: Courts of Noida, Uttar Pradesh

---

## 11. PROHIBITED ACTIVITIES

Users must NOT:
- Provide false or misleading information
- Use Platform for illegal activities
- Harass, abuse, or threaten other users
- Attempt to bypass payment systems
- Create multiple accounts to abuse promotions
- Share account credentials
- Scrape or copy Platform content
- Reverse engineer Platform technology
- Post spam or unauthorized advertisements
- Violate intellectual property rights
- Engage in fraudulent activities

Violation may result in account suspension, legal action, and liability for damages.

---

## 12. INTELLECTUAL PROPERTY

### 12.1 Platform Ownership

All Platform content, including:
- Software and code
- Design and layout
- Logos and trademarks
- Text, images, and videos
- Algorithms and processes

are owned by ConvergeAI or licensed to us. Unauthorized use is prohibited.

### 12.2 User Content

By posting content (reviews, photos, etc.), you grant us:
- Non-exclusive, worldwide, royalty-free license
- Right to use, modify, and display content
- Right to use for marketing and promotional purposes

You retain ownership of your content.

### 12.3 Trademark Usage

"ConvergeAI" and related marks are our trademarks. Use without permission is prohibited.

---

## 13. LIMITATION OF LIABILITY

### 13.1 Platform Liability

TO THE MAXIMUM EXTENT PERMITTED BY LAW:
- We are not liable for Service Provider actions or omissions
- We do not guarantee service quality or outcomes
- We are not responsible for property damage or personal injury
- Our liability is limited to the amount paid for the specific service

### 13.2 Disclaimer of Warranties

THE PLATFORM IS PROVIDED "AS IS" WITHOUT WARRANTIES OF ANY KIND, EXPRESS OR IMPLIED.

### 13.3 Indemnification

You agree to indemnify and hold us harmless from claims arising from:
- Your use of the Platform
- Your violation of these Terms
- Your violation of third-party rights

---

## 14. PRIVACY AND DATA PROTECTION

### 14.1 Data Collection

We collect and process personal data as described in our Privacy Policy.

### 14.2 Data Security

We implement industry-standard security measures to protect your data.

### 14.3 Data Sharing

We may share data with:
- Service Providers (for service delivery)
- Payment processors
- Government authorities (when required by law)
- Third-party service providers (with your consent)

---

## 15. GENERAL PROVISIONS

### 15.1 Governing Law

These Terms are governed by the laws of India.

### 15.2 Jurisdiction

Courts of Noida, Uttar Pradesh have exclusive jurisdiction.

### 15.3 Severability

If any provision is found invalid, remaining provisions remain in effect.

### 15.4 Entire Agreement

These Terms constitute the entire agreement between you and ConvergeAI.

### 15.5 Contact Information

For questions or concerns:

**{COMPANY_INFO['name']}**  
{COMPANY_INFO['address']}  
Email: {COMPANY_INFO['email']}  
Phone: {COMPANY_INFO['phone']}  
Website: {COMPANY_INFO['website']}

---

**By using the ConvergeAI Platform, you acknowledge that you have read, understood, and agree to be bound by these Terms and Conditions.**

---

*Document Version: 1.0*  
*Effective Date: {COMPANY_INFO['effective_date']}*  
*Last Updated: {COMPANY_INFO['last_updated']}*
"""
    
    filepath = DOCS_DIR / "01_Terms_and_Conditions.md"
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content.strip())
    
    print(f"✅ Generated: {filepath}")
    return filepath


def generate_privacy_policy():
    """Generate comprehensive Privacy Policy"""
    content = f"""
# PRIVACY POLICY

**{COMPANY_INFO['brand']} - Service Marketplace Platform**

**Effective Date**: {COMPANY_INFO['effective_date']}
**Last Updated**: {COMPANY_INFO['last_updated']}

---

## 1. INTRODUCTION

{COMPANY_INFO['name']} ("we", "us", "our") respects your privacy and is committed to protecting your personal data. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our Platform.

### 1.1 Scope

This Privacy Policy applies to:
- ConvergeAI website (www.convergeai.com)
- ConvergeAI mobile applications (iOS and Android)
- All related services and features

### 1.2 Consent

By using our Platform, you consent to the collection and use of your information as described in this Privacy Policy.

### 1.3 Updates

We may update this Privacy Policy from time to time. Material changes will be notified through email or prominent notice on the Platform.

---

## 2. INFORMATION WE COLLECT

### 2.1 Information You Provide

**Account Information**:
- Full name
- Mobile number (mandatory)
- Email address
- Date of birth
- Gender
- Profile photo

**Service Address Information**:
- Complete address
- Landmark
- Pincode
- GPS coordinates (with permission)
- Address type (home, office, other)

**Payment Information**:
- Credit/debit card details (tokenized)
- Bank account information (for refunds)
- UPI ID
- Wallet information
- Billing address

**Service Provider Information** (additional):
- Government-issued ID (Aadhaar, PAN, Driving License)
- Professional certifications
- Bank account details
- GST number (if applicable)
- Background verification documents
- Work experience and skills
- Service area preferences

**Communication Data**:
- Customer support conversations
- Chat messages with Service Providers
- Complaint details
- Feedback and reviews
- Survey responses

### 2.2 Information Collected Automatically

**Device Information**:
- Device type and model
- Operating system and version
- Unique device identifiers
- Mobile network information
- IP address
- Browser type and version

**Usage Information**:
- Pages visited
- Features used
- Time spent on Platform
- Search queries
- Booking history
- Click patterns
- App interactions

**Location Information**:
- Precise location (GPS) - with permission
- Approximate location (IP-based)
- Service delivery locations
- Service Provider location (during service)

**Cookies and Similar Technologies**:
- Session cookies
- Persistent cookies
- Web beacons
- Local storage
- Analytics cookies

### 2.3 Information from Third Parties

**Social Media**:
- Profile information (if you sign in via social media)
- Friends list (with permission)
- Email address

**Payment Processors**:
- Transaction status
- Payment method details
- Fraud detection information

**Background Verification Agencies** (for Service Providers):
- Criminal record checks
- Identity verification
- Address verification
- Employment history

**Government Databases**:
- Aadhaar verification (with consent)
- PAN verification
- GST verification

---

## 3. HOW WE USE YOUR INFORMATION

### 3.1 Service Delivery

- Create and manage your account
- Process bookings and payments
- Match Customers with Service Providers
- Facilitate communication between parties
- Send booking confirmations and reminders
- Provide customer support
- Process refunds and cancellations

### 3.2 Platform Improvement

- Analyze usage patterns
- Improve user experience
- Develop new features
- Conduct research and analytics
- Test new functionality
- Optimize performance

### 3.3 Safety and Security

- Verify user identity
- Prevent fraud and abuse
- Detect and prevent security threats
- Enforce Terms and Conditions
- Comply with legal obligations
- Resolve disputes

### 3.4 Marketing and Communications

- Send promotional offers and discounts
- Notify about new services
- Share platform updates
- Conduct surveys and feedback requests
- Send newsletters (with consent)
- Personalize marketing content

You can opt-out of marketing communications at any time.

### 3.5 Legal Compliance

- Comply with applicable laws and regulations
- Respond to legal requests and court orders
- Protect our rights and property
- Enforce our Terms and Conditions
- Cooperate with law enforcement

---

## 4. HOW WE SHARE YOUR INFORMATION

### 4.1 With Service Providers

We share necessary information with Service Providers to facilitate service delivery:
- Customer name and contact number
- Service address
- Service details and requirements
- Special instructions

### 4.2 With Customers

Service Providers' information shared with Customers:
- Name and photo
- Ratings and reviews
- Service specializations
- Approximate location (during service)

### 4.3 With Service Partners

**Payment Processors**:
- Transaction details
- Payment method information
- Billing address

**SMS and Email Service Providers**:
- Mobile number
- Email address
- Message content

**Analytics Providers**:
- Usage data
- Device information
- Anonymized user behavior

**Cloud Storage Providers**:
- Encrypted data backups
- Application logs

### 4.4 With Government Authorities

When required by law:
- Tax authorities (GST, Income Tax)
- Law enforcement agencies
- Regulatory bodies
- Courts and tribunals

### 4.5 Business Transfers

In case of merger, acquisition, or sale:
- User data may be transferred
- You will be notified of any such transfer
- Privacy Policy will continue to apply

### 4.6 With Your Consent

We may share information with third parties when you explicitly consent.

---

## 5. DATA SECURITY

### 5.1 Security Measures

We implement industry-standard security measures:

**Technical Safeguards**:
- SSL/TLS encryption for data transmission
- AES-256 encryption for data at rest
- Secure authentication mechanisms
- Regular security audits
- Intrusion detection systems
- Firewall protection

**Organizational Safeguards**:
- Access controls and authorization
- Employee training on data protection
- Confidentiality agreements
- Regular security assessments
- Incident response procedures

**Payment Security**:
- PCI-DSS compliance
- Tokenization of card details
- Secure payment gateways
- No storage of CVV/PIN

### 5.2 Data Retention

We retain your data for as long as:
- Your account is active
- Required to provide services
- Required by law
- Necessary for legitimate business purposes

After account deletion:
- Personal data deleted within 90 days
- Transaction records retained for 7 years (tax compliance)
- Anonymized data may be retained for analytics

### 5.3 Your Responsibilities

- Keep your password secure
- Do not share account credentials
- Log out after using shared devices
- Report suspicious activity immediately
- Keep your contact information updated

---

## 6. YOUR RIGHTS AND CHOICES

### 6.1 Access and Correction

You have the right to:
- Access your personal data
- Correct inaccurate information
- Update your profile
- Download your data

Access through: Account Settings or contact support@convergeai.com

### 6.2 Data Deletion

You can request deletion of your account and data:
- Through Account Settings
- By emailing privacy@convergeai.com
- Some data may be retained for legal compliance

### 6.3 Marketing Opt-Out

You can opt-out of marketing communications:
- Click "Unsubscribe" in emails
- Adjust notification settings in app
- Contact support@convergeai.com

You will still receive transactional messages (booking confirmations, etc.)

### 6.4 Cookie Management

You can control cookies through:
- Browser settings
- Cookie preference center on website
- Mobile app settings

Note: Disabling cookies may affect Platform functionality.

### 6.5 Location Services

You can control location access:
- Through device settings
- Through app permissions
- By denying location access

Note: Some features require location access.

---

## 7. CHILDREN'S PRIVACY

Our Platform is not intended for users under 18 years of age. We do not knowingly collect personal information from children. If we discover that we have collected information from a child, we will delete it immediately.

---

## 8. INTERNATIONAL DATA TRANSFERS

Your data may be transferred to and processed in countries other than India. We ensure adequate safeguards are in place through:
- Standard contractual clauses
- Data processing agreements
- Compliance with applicable data protection laws

---

## 9. THIRD-PARTY LINKS

Our Platform may contain links to third-party websites or services. We are not responsible for their privacy practices. We encourage you to read their privacy policies.

---

## 10. CHANGES TO THIS PRIVACY POLICY

We may update this Privacy Policy from time to time. We will notify you of material changes through:
- Email notification
- Prominent notice on Platform
- In-app notification

Continued use after changes constitutes acceptance.

---

## 11. CONTACT US

For privacy-related questions or concerns:

**Data Protection Officer**
{COMPANY_INFO['name']}
{COMPANY_INFO['address']}
Email: privacy@convergeai.com
Phone: {COMPANY_INFO['phone']}

For data access, correction, or deletion requests:
Email: privacy@convergeai.com

---

## 12. GRIEVANCE OFFICER

As per Information Technology Act, 2000:

**Grievance Officer**
Name: [Grievance Officer Name]
Email: grievance@convergeai.com
Phone: {COMPANY_INFO['phone']}
Address: {COMPANY_INFO['address']}

Grievances will be acknowledged within 24 hours and resolved within 30 days.

---

**By using the ConvergeAI Platform, you acknowledge that you have read and understood this Privacy Policy.**

---

*Document Version: 1.0*
*Effective Date: {COMPANY_INFO['effective_date']}*
*Last Updated: {COMPANY_INFO['last_updated']}*
"""

    filepath = DOCS_DIR / "02_Privacy_Policy.md"
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content.strip())

    print(f"✅ Generated: {filepath}")
    return filepath


if __name__ == "__main__":
    print("=" * 80)
    print("GENERATING POLICY DOCUMENTS FOR CONVERGEAI")
    print("=" * 80)
    print()

    # Generate all documents
    generate_terms_and_conditions()
    generate_privacy_policy()

    print()
    print("=" * 80)
    print("DOCUMENT GENERATION COMPLETE")
    print(f"Documents saved to: {DOCS_DIR}")
    print("=" * 80)

