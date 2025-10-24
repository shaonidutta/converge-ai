"""
Intent Classification Examples

Few-shot examples for each intent to improve LLM classification accuracy.
These examples are used when pattern matching is insufficient.
"""

from typing import Dict, List
from .config import IntentType


# Few-shot examples for each intent (10-15 examples per intent)
INTENT_EXAMPLES: Dict[IntentType, List[str]] = {
    IntentType.BOOKING_MANAGEMENT: [
        "I want to book an AC service for tomorrow",
        "Can you schedule a plumber for next Monday?",
        "Book cleaning service for my home",
        "I need AC repair urgently",
        "Schedule washing machine service",
        "Cancel my booking for tomorrow",
        "I want to cancel my appointment",
        "Cancel the service scheduled for Friday",
        "Reschedule my booking to next week",
        "Can I change my appointment time?",
        "Move my booking to another date",
        "Modify my service booking",
        "Update my appointment details",
        "What's the status of my booking?",
        "Check my booking status"
    ],
    
    IntentType.PRICING_INQUIRY: [
        "How much does AC servicing cost?",
        "What's the price for plumbing?",
        "Tell me the rates for cleaning",
        "What are your charges?",
        "Price for AC installation?",
        "How much do you charge for electrical work?",
        "What's the cost of painting a room?",
        "Charges for deep cleaning?",
        "What are the rates for appliance repair?",
        "How much for pest control service?",
        "Price list for your services",
        "Cost of AC repair",
        "What do you charge for plumbing services?"
    ],
    
    IntentType.AVAILABILITY_CHECK: [
        "Are you available tomorrow?",
        "When can you come for AC service?",
        "Do you have any slots available this week?",
        "Check availability for plumbing service",
        "When is the earliest you can come?",
        "Available times for cleaning service?",
        "Do you have technicians available today?",
        "Can someone come this evening?",
        "What slots are free on Monday?",
        "Check if you're available on the weekend",
        "When can I get AC service done?",
        "Available dates for painting service"
    ],
    
    IntentType.SERVICE_INFORMATION: [
        "What does AC servicing include?",
        "Tell me about your cleaning service",
        "What's included in deep cleaning?",
        "Explain the AC installation process",
        "How does plumbing service work?",
        "What do you do in electrical service?",
        "Details about painting service",
        "Information about pest control",
        "What's the process for appliance repair?",
        "How long does AC servicing take?",
        "What should I prepare before the service?",
        "Tell me about your warranty",
        "What are the benefits of regular AC maintenance?",
        "can u help with services?",
        "what services do you offer?",
        "help me with services",
        "show me available services",
        "what kind of services are available?"
    ],
    
    IntentType.COMPLAINT: [
        "I want to file a complaint",
        "The service quality was very poor",
        "The technician was rude to me",
        "My AC is still not working after service",
        "The technician damaged my furniture",
        "Very disappointed with the service",
        "The technician came 2 hours late",
        "The technician didn't show up",
        "Complaint about poor service quality",
        "The work was not done properly",
        "Technician was unprofessional",
        "I'm not satisfied with the service",
        "The technician broke my AC",
        "Service was incomplete"
    ],
    
    IntentType.PAYMENT_ISSUE: [
        "My payment failed",
        "Payment is not working",
        "I was charged twice",
        "Double payment deducted",
        "Wrong amount was charged",
        "I was overcharged",
        "Payment declined but money deducted",
        "Transaction failed",
        "Payment error occurred",
        "I can't make payment",
        "Payment method not working",
        "Card payment failed",
        "UPI payment issue"
    ],
    
    IntentType.REFUND_REQUEST: [
        "I want a refund",
        "Give me my money back",
        "Refund my payment",
        "I need a refund",
        "Request for refund",
        "How do I get a refund?",
        "Refund to my wallet",
        "When will I get my refund?",
        "Refund status",
        "I want my money back",
        "Process my refund",
        "Refund for cancelled booking",
        "Partial refund request"
    ],
    
    IntentType.ACCOUNT_MANAGEMENT: [
        "Update my profile",
        "Change my phone number",
        "Update my email address",
        "Change my address",
        "Manage my account",
        "Update my details",
        "Delete my account",
        "Change my password",
        "Update my profile information",
        "Add a new address",
        "Remove my old address",
        "Update my preferences"
    ],
    
    IntentType.TRACK_SERVICE: [
        "Where is the technician?",
        "Track my technician",
        "When will the technician arrive?",
        "Technician ETA",
        "Track my booking",
        "Where is my service technician?",
        "How far is the technician?",
        "Technician location",
        "When will he reach?",
        "Track technician location",
        "Service status",
        "Is the technician on the way?"
    ],
    
    IntentType.FEEDBACK: [
        "I want to give feedback",
        "Rate the service",
        "Write a review",
        "Provide feedback",
        "The service was excellent",
        "Great service, thank you",
        "I want to rate the technician",
        "Leave a review",
        "Compliment the technician",
        "The technician was very professional",
        "5 star service",
        "Very satisfied with the service"
    ],
    
    IntentType.POLICY_INQUIRY: [
        "What's your cancellation policy?",
        "Tell me about refund policy",
        "What's your warranty policy?",
        "Terms and conditions",
        "Privacy policy",
        "Cancellation charges",
        "Refund policy details",
        "What's your guarantee?",
        "Service warranty information",
        "Rescheduling policy",
        "Late cancellation fee",
        "What are your terms?"
    ],
    
    IntentType.GREETING: [
        "Hello",
        "Hi there",
        "Hey",
        "Good morning",
        "Good afternoon",
        "Good evening",
        "Namaste",
        "Greetings",
        "Hi, how are you?",
        "Hello, I need help"
    ],
    
    IntentType.GENERAL_QUERY: [
        "How does your platform work?",
        "What services do you offer?",
        "Tell me about your company",
        "How can I use your app?",
        "What areas do you serve?",
        "Do you have an app?",
        "How to contact support?",
        "What are your working hours?",
        "Do you provide emergency services?",
        "Are you available on weekends?"
    ],
}


# Multi-intent examples (queries with multiple intents)
MULTI_INTENT_EXAMPLES: List[Dict[str, any]] = [
    {
        "query": "I want to book AC service and know the price",
        "intents": [
            {"intent": IntentType.BOOKING_MANAGEMENT, "confidence": 0.9},
            {"intent": IntentType.PRICING_INQUIRY, "confidence": 0.85}
        ]
    },
    {
        "query": "Cancel my booking and give me a refund",
        "intents": [
            {"intent": IntentType.BOOKING_MANAGEMENT, "confidence": 0.95},
            {"intent": IntentType.REFUND_REQUEST, "confidence": 0.9}
        ]
    },
    {
        "query": "What's the price and when are you available?",
        "intents": [
            {"intent": IntentType.PRICING_INQUIRY, "confidence": 0.9},
            {"intent": IntentType.AVAILABILITY_CHECK, "confidence": 0.85}
        ]
    },
    {
        "query": "Book plumbing service and tell me what's included",
        "intents": [
            {"intent": IntentType.BOOKING_MANAGEMENT, "confidence": 0.9},
            {"intent": IntentType.SERVICE_INFORMATION, "confidence": 0.8}
        ]
    },
    {
        "query": "I have a complaint and want a refund",
        "intents": [
            {"intent": IntentType.COMPLAINT, "confidence": 0.95},
            {"intent": IntentType.REFUND_REQUEST, "confidence": 0.9}
        ]
    },
]


def get_examples_for_intent(intent: IntentType) -> List[str]:
    """
    Get example queries for a specific intent
    
    Args:
        intent: Intent type
        
    Returns:
        List of example queries
    """
    return INTENT_EXAMPLES.get(intent, [])


def get_all_examples() -> Dict[IntentType, List[str]]:
    """
    Get all intent examples
    
    Returns:
        Dictionary mapping intent to example queries
    """
    return INTENT_EXAMPLES


def get_multi_intent_examples() -> List[Dict[str, any]]:
    """
    Get examples of queries with multiple intents
    
    Returns:
        List of multi-intent examples
    """
    return MULTI_INTENT_EXAMPLES

