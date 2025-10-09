"""
LLM Prompts for Intent Classification

Prompt templates for intent classification and entity extraction.
"""

import json
from typing import Dict, List, Optional, Any
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


def build_context_aware_intent_prompt(
    user_message: str,
    conversation_history: Optional[List[Dict[str, str]]] = None,
    dialog_state: Optional[Any] = None
) -> str:
    """
    Build a context-aware prompt for intent classification

    This prompt includes conversation history and dialog state to help
    the LLM understand follow-up responses like "yes", "tomorrow", etc.

    Args:
        user_message: Current user message to classify
        conversation_history: Previous messages in the conversation
            Format: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
        dialog_state: Active dialog state with collected entities and context

    Returns:
        Formatted context-aware prompt string
    """
    # Get all intent examples
    examples = get_all_examples()

    # Build intent descriptions
    intent_descriptions = []
    for intent_type, config in INTENT_CONFIGS.items():
        intent_descriptions.append(
            f"- **{intent_type.value}**: {config.description}"
        )

    # Build conversation context section
    context_section = ""

    if conversation_history:
        context_section += "\n**Conversation History:**\n"
        # Show last 5 messages for context
        recent_history = conversation_history[-5:] if len(conversation_history) > 5 else conversation_history
        for msg in recent_history:
            role = msg.get("role", "unknown").capitalize()
            content = msg.get("content", "")
            context_section += f"{role}: \"{content}\"\n"

    if dialog_state:
        context_section += "\n**Active Dialog State:**\n"
        context_section += f"- Current State: {dialog_state.state.value}\n"
        if dialog_state.intent:
            context_section += f"- Intent: {dialog_state.intent}\n"
        if dialog_state.collected_entities:
            context_section += f"- Collected Entities: {json.dumps(dialog_state.collected_entities)}\n"
        if dialog_state.needed_entities:
            context_section += f"- Still Needed: {', '.join(dialog_state.needed_entities)}\n"
        if dialog_state.context and dialog_state.context.get('last_question'):
            context_section += f"- Last Question Asked: \"{dialog_state.context['last_question']}\"\n"

    prompt = f"""You are an expert intent classifier for a home services platform.

Your task is to analyze user queries IN CONTEXT and identify ALL intents present in the message.

**IMPORTANT - Context-Aware Classification:**
- The user's current message may be a FOLLOW-UP RESPONSE to a previous question
- Short responses like "yes", "no", "tomorrow", "2 PM" should be interpreted based on the conversation context
- If there's an active dialog state, the user is likely providing information for that ongoing conversation
- Consider what information is still needed (needed_entities) when interpreting the message

**Available Intents:**
{chr(10).join(intent_descriptions)}
{context_section}

**Current User Message:**
"{user_message}"

**Instructions:**
1. **First**, check if this is a follow-up response:
   - Is there an active dialog state?
   - Does the message answer the last question asked?
   - Is the message providing a needed entity?

2. **If it's a follow-up response:**
   - Keep the same intent as the active dialog state
   - Extract the entity value from the message
   - Mark confidence as high (0.9+) if it clearly answers the question

3. **If it's a NEW intent:**
   - Identify all intents in the message
   - Extract relevant entities
   - Assign appropriate confidence scores

4. **Entity Extraction:**
   - Extract entities relevant to the detected intent
   - Use context to resolve ambiguous references (e.g., "that" referring to a service mentioned earlier)

**Your Response:**
Return a JSON object with the following structure:
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
    "clarification_reason": "",
    "context_used": true,
    "context_summary": "3 previous messages, active dialog state (collecting_info)"
}}

Return ONLY the JSON object, no additional text.
"""

    return prompt


def get_system_prompt(prompt_type: str) -> str:
    """
    Get system prompt for a specific use case

    Args:
        prompt_type: Type of prompt (intent_classification, entity_extraction, clarification)

    Returns:
        System prompt string
    """
    return SYSTEM_PROMPTS.get(prompt_type, SYSTEM_PROMPTS["intent_classification"])

