"""
Intent Classification Configuration

Defines core intents, entity types, and classification settings
for the multi-intent classification system.
"""

from enum import Enum
from typing import Dict, List, Set
from pydantic import BaseModel, Field


class IntentType(str, Enum):
    """Core intent types for the home services platform"""
    
    # Booking & Scheduling
    BOOKING_MANAGEMENT = "booking_management"
    
    # Pricing & Availability
    PRICING_INQUIRY = "pricing_inquiry"
    AVAILABILITY_CHECK = "availability_check"
    
    # Service Information
    SERVICE_INFORMATION = "service_information"
    
    # Complaints & Issues
    COMPLAINT = "complaint"
    
    # Payment & Billing
    PAYMENT_ISSUE = "payment_issue"
    
    # Refunds & Credits
    REFUND_REQUEST = "refund_request"
    
    # Account Management
    ACCOUNT_MANAGEMENT = "account_management"
    
    # Tracking & Real-time
    TRACK_SERVICE = "track_service"
    
    # Feedback & Ratings
    FEEDBACK = "feedback"
    
    # Policy Information
    POLICY_INQUIRY = "policy_inquiry"
    
    # Conversational
    GREETING = "greeting"
    GENERAL_QUERY = "general_query"
    
    # Special Cases
    OUT_OF_SCOPE = "out_of_scope"
    UNCLEAR_INTENT = "unclear_intent"


class EntityType(str, Enum):
    """Entity types that can be extracted from user messages"""
    
    # Action entities
    ACTION = "action"  # book, cancel, reschedule, modify, check_status
    
    # Service entities
    SERVICE_TYPE = "service_type"  # AC, plumbing, cleaning, electrical, etc.
    SERVICE_SUBCATEGORY = "service_subcategory"  # Interior painting, exterior painting, etc.
    
    # Issue entities
    ISSUE_TYPE = "issue_type"  # quality, behavior, damage, late, no_show
    
    # Payment entities
    PAYMENT_TYPE = "payment_type"  # failed, double_charged, wrong_amount, method
    
    # Refund entities
    REFUND_TYPE = "refund_type"  # full, partial, wallet
    
    # Account entities
    ACCOUNT_FIELD = "account_field"  # profile, address, phone, email
    
    # Temporal entities
    DATE = "date"
    TIME = "time"
    
    # Location entities
    LOCATION = "location"
    ADDRESS_LINE1 = "address_line1"
    ADDRESS_LINE2 = "address_line2"
    CITY = "city"
    STATE = "state"

    # Identifiers
    BOOKING_ID = "booking_id"
    TRANSACTION_ID = "transaction_id"
    
    # Feedback entities
    RATING = "rating"
    FEEDBACK_TYPE = "feedback_type"  # rate, review, compliment
    
    # Policy entities
    POLICY_TYPE = "policy_type"  # cancellation, refund, warranty, terms, privacy
    
    # Info type entities
    INFO_TYPE = "info_type"  # details, duration, process, requirements

    # Booking filter entities
    STATUS_FILTER = "status_filter"  # pending, confirmed, completed, cancelled
    SORT_BY = "sort_by"  # date, status, amount
    LIMIT = "limit"  # number of results


class IntentConfig(BaseModel):
    """Configuration for a specific intent"""
    
    intent: IntentType
    description: str
    required_entities: List[EntityType] = Field(default_factory=list)
    optional_entities: List[EntityType] = Field(default_factory=list)
    agent: str  # Which agent handles this intent
    priority: int = 1  # Higher priority intents are processed first


# Intent configurations
INTENT_CONFIGS: Dict[IntentType, IntentConfig] = {
    IntentType.BOOKING_MANAGEMENT: IntentConfig(
        intent=IntentType.BOOKING_MANAGEMENT,
        description="User wants to book, cancel, reschedule, or modify a service booking",
        required_entities=[EntityType.ACTION],  # Only ACTION is required; other entities depend on the action
        optional_entities=[
            EntityType.SERVICE_TYPE,
            EntityType.BOOKING_ID,
            EntityType.LOCATION,
            EntityType.DATE,
            EntityType.TIME,
            EntityType.ADDRESS_LINE1,
            EntityType.ADDRESS_LINE2,
            EntityType.CITY,
            EntityType.STATE,
            EntityType.STATUS_FILTER,
            EntityType.SORT_BY,
            EntityType.LIMIT
        ],
        agent="BookingAgent",
        priority=10
    ),
    IntentType.PRICING_INQUIRY: IntentConfig(
        intent=IntentType.PRICING_INQUIRY,
        description="User wants to know the price or cost of a service",
        optional_entities=[EntityType.SERVICE_TYPE, EntityType.LOCATION],
        agent="SQLAgent",
        priority=8
    ),
    IntentType.AVAILABILITY_CHECK: IntentConfig(
        intent=IntentType.AVAILABILITY_CHECK,
        description="User wants to check service availability or technician availability",
        optional_entities=[EntityType.SERVICE_TYPE, EntityType.DATE, EntityType.TIME, EntityType.LOCATION],
        agent="SQLAgent",
        priority=8
    ),
    IntentType.SERVICE_INFORMATION: IntentConfig(
        intent=IntentType.SERVICE_INFORMATION,
        description="User wants information about services offered, service categories, what services are available, or help with services",
        optional_entities=[EntityType.SERVICE_TYPE, EntityType.INFO_TYPE],
        agent="ServiceAgent",  # Fixed: was "RAGAgent", should be "ServiceAgent"
        priority=7
    ),
    IntentType.COMPLAINT: IntentConfig(
        intent=IntentType.COMPLAINT,
        description="User has a complaint or issue with service quality, technician behavior, or damage",
        required_entities=[EntityType.ISSUE_TYPE],
        optional_entities=[EntityType.BOOKING_ID, EntityType.SERVICE_TYPE],
        agent="ComplaintAgent",
        priority=10
    ),
    IntentType.PAYMENT_ISSUE: IntentConfig(
        intent=IntentType.PAYMENT_ISSUE,
        description="User has a payment-related issue (failed payment, double charge, wrong amount)",
        required_entities=[EntityType.PAYMENT_TYPE],
        optional_entities=[EntityType.TRANSACTION_ID, EntityType.BOOKING_ID],
        agent="PaymentAgent",
        priority=9
    ),
    IntentType.REFUND_REQUEST: IntentConfig(
        intent=IntentType.REFUND_REQUEST,
        description="User wants a refund (full, partial, or to wallet)",
        optional_entities=[EntityType.REFUND_TYPE, EntityType.BOOKING_ID, EntityType.TRANSACTION_ID],
        agent="RefundAgent",
        priority=9
    ),
    IntentType.ACCOUNT_MANAGEMENT: IntentConfig(
        intent=IntentType.ACCOUNT_MANAGEMENT,
        description="User wants to manage their account (update profile, address, phone, email)",
        required_entities=[EntityType.ACTION],
        optional_entities=[EntityType.ACCOUNT_FIELD],
        agent="AccountAgent",
        priority=6
    ),
    IntentType.TRACK_SERVICE: IntentConfig(
        intent=IntentType.TRACK_SERVICE,
        description="User wants to track technician location, ETA, or service status",
        optional_entities=[EntityType.BOOKING_ID, EntityType.INFO_TYPE],
        agent="TrackingAgent",
        priority=8
    ),
    IntentType.FEEDBACK: IntentConfig(
        intent=IntentType.FEEDBACK,
        description="User wants to provide feedback, rating, or review",
        optional_entities=[EntityType.FEEDBACK_TYPE, EntityType.RATING, EntityType.BOOKING_ID],
        agent="FeedbackAgent",
        priority=5
    ),
    IntentType.POLICY_INQUIRY: IntentConfig(
        intent=IntentType.POLICY_INQUIRY,
        description="User wants information about policies (cancellation, refund, warranty, terms, privacy)",
        optional_entities=[EntityType.POLICY_TYPE],
        agent="PolicyAgent",
        priority=7
    ),
    IntentType.GREETING: IntentConfig(
        intent=IntentType.GREETING,
        description="User is greeting or starting a conversation",
        agent="Coordinator",
        priority=3
    ),
    IntentType.GENERAL_QUERY: IntentConfig(
        intent=IntentType.GENERAL_QUERY,
        description="General question that doesn't fit other categories",
        agent="Coordinator",
        priority=2
    ),
    IntentType.OUT_OF_SCOPE: IntentConfig(
        intent=IntentType.OUT_OF_SCOPE,
        description="Query is outside the scope of home services platform",
        agent="Coordinator",
        priority=1
    ),
    IntentType.UNCLEAR_INTENT: IntentConfig(
        intent=IntentType.UNCLEAR_INTENT,
        description="Intent is unclear and needs clarification",
        agent="Coordinator",
        priority=1
    ),
}


# Classification thresholds
class ClassificationThresholds:
    """Confidence thresholds for intent classification"""
    
    # Pattern matching threshold (high confidence)
    PATTERN_MATCH_THRESHOLD = 0.9
    
    # LLM classification threshold (medium confidence)
    LLM_CLASSIFICATION_THRESHOLD = 0.7
    
    # Minimum confidence for secondary intents
    SECONDARY_INTENT_THRESHOLD = 0.6
    
    # Threshold for requiring clarification
    CLARIFICATION_THRESHOLD = 0.5
    
    # Maximum number of intents to return
    MAX_INTENTS = 3


# Service type mappings
SERVICE_TYPES: Set[str] = {
    "ac", "air_conditioning", "hvac",
    "plumbing", "plumber",
    "cleaning", "house_cleaning", "deep_cleaning",
    "electrical", "electrician",
    "painting", "painter",
    "carpentry", "carpenter",
    "appliance_repair", "washing_machine", "refrigerator",
    "pest_control",
    "home_repair", "handyman"
}


# Action mappings
ACTIONS: Dict[str, Set[str]] = {
    "book": {"book", "schedule", "arrange", "set_up", "appointment"},
    "cancel": {"cancel", "remove", "delete", "abort"},
    "reschedule": {"reschedule", "change", "move", "shift"},
    "modify": {"modify", "update", "edit", "change"},
    "list": {"list", "show", "view", "display", "see", "get", "my bookings", "all bookings"},
    "check_status": {"status", "check", "track", "where", "when"}
}


# Issue type mappings
ISSUE_TYPES: Set[str] = {
    "quality", "poor_quality", "bad_service",
    "behavior", "rude", "unprofessional",
    "damage", "broken", "damaged",
    "late", "delayed", "not_on_time",
    "no_show", "didn't_come", "missed"
}


# Payment issue mappings
PAYMENT_ISSUES: Set[str] = {
    "failed", "declined", "not_working",
    "double_charged", "charged_twice",
    "wrong_amount", "overcharged", "incorrect_charge",
    "payment_method", "card", "upi", "wallet"
}

