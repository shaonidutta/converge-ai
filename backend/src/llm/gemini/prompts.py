"""
LLM Prompts for Intent Classification

Prompt templates for intent classification and entity extraction.
"""

import json
from typing import Dict, List
from src.nlp.intent.config import IntentType, INTENT_CONFIGS
from src.nlp.intent.examples import get_all_examples


def build_intent_classification_prompt(user_message: str) -> str:
    """
    Build a prompt for multi-intent classification with few-shot examples
    
    Args:
        user_message: User's message to classify
        
    Returns:
        Formatted prompt string
    """
    # Get all intent examples
    examples = get_all_examples()
    
    # Build intent descriptions
    intent_descriptions = []
    for intent_type, config in INTENT_CONFIGS.items():
        intent_descriptions.append(
            f"- **{intent_type.value}**: {config.description}"
        )
    
    # Build few-shot examples (2-3 examples per intent for brevity)
    few_shot_examples = []
    for intent_type, example_queries in examples.items():
        # Take first 2 examples for each intent
        for query in example_queries[:2]:
            few_shot_examples.append(
                f'User: "{query}"\nIntent: {intent_type.value}'
            )
    
    prompt = f"""You are an expert intent classifier for a home services platform.

Your task is to analyze user queries and identify ALL intents present in the message.
A query can have multiple intents (e.g., "book AC service and tell me the price" has both booking_management and pricing_inquiry intents).

**Available Intents:**
{chr(10).join(intent_descriptions)}

**Few-Shot Examples:**
{chr(10).join(few_shot_examples[:20])}  # Limit to 20 examples to keep prompt concise

**Instructions:**
1. Identify ALL intents present in the user's message
2. Assign a confidence score (0.0 to 1.0) for each detected intent
3. Extract relevant entities (service_type, action, date, time, location, booking_id, etc.)
4. If the query is unclear or ambiguous, mark it as "unclear_intent"
5. If the query is outside the scope of home services, mark it as "out_of_scope"

**User Query:**
"{user_message}"

**Your Response:**
Analyze the query and return a JSON object with the following structure:
{{
    "intents": [
        {{
            "intent": "intent_name",
            "confidence": 0.95,
            "entities": {{
                "entity_type": "entity_value"
            }}
        }}
    ],
    "primary_intent": "intent_name",
    "requires_clarification": false,
    "clarification_reason": ""
}}

Return ONLY the JSON object, no additional text.
"""
    
    return prompt


def build_entity_extraction_prompt(user_message: str, intent: str) -> str:
    """
    Build a prompt for entity extraction given a specific intent
    
    Args:
        user_message: User's message
        intent: Detected intent
        
    Returns:
        Formatted prompt string
    """
    prompt = f"""You are an expert entity extractor for a home services platform.

Given the user's message and the detected intent, extract all relevant entities.

**Intent:** {intent}

**User Message:** "{user_message}"

**Entities to Extract (if present):**
- service_type: Type of service (AC, plumbing, cleaning, electrical, etc.)
- action: Action to perform (book, cancel, reschedule, modify, check_status)
- date: Date mentioned (extract in ISO format if possible)
- time: Time mentioned
- location: Location or address
- booking_id: Booking reference ID
- transaction_id: Transaction reference ID
- issue_type: Type of issue (quality, behavior, damage, late, no_show)
- payment_type: Payment issue type (failed, double_charged, wrong_amount)
- refund_type: Refund type (full, partial, wallet)
- rating: Rating value (1-5)
- policy_type: Policy type (cancellation, refund, warranty, terms, privacy)

**Your Response:**
Return a JSON object with extracted entities:
{{
    "entities": {{
        "entity_type": "entity_value"
    }}
}}

Return ONLY the JSON object, no additional text.
"""
    
    return prompt


# System prompts for different use cases
SYSTEM_PROMPTS = {
    "intent_classification": """You are an expert intent classifier for a home services platform.
Your role is to accurately identify user intents and extract relevant entities.
Always be precise and return structured JSON output.""",
    
    "entity_extraction": """You are an expert entity extractor for a home services platform.
Your role is to extract all relevant entities from user messages based on the detected intent.
Always return structured JSON output with extracted entities.""",
    
    "clarification": """You are a helpful assistant for a home services platform.
When user intent is unclear, ask clarifying questions to better understand their needs.
Be polite, concise, and helpful."""
}


def get_system_prompt(prompt_type: str) -> str:
    """
    Get system prompt for a specific use case
    
    Args:
        prompt_type: Type of prompt (intent_classification, entity_extraction, clarification)
        
    Returns:
        System prompt string
    """
    return SYSTEM_PROMPTS.get(prompt_type, SYSTEM_PROMPTS["intent_classification"])

