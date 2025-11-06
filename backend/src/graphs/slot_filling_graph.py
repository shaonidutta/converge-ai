"""
Slot-Filling Graph (Graph 1)

Handles multi-turn conversations to collect required entities.

Flow:
1. Classify intent (context-aware)
2. Check if follow-up response
3. If follow-up: Extract entity → Validate → Update state
4. If new intent: Determine needed entities → Generate question
5. If all entities collected: Trigger Agent Execution Graph
6. If more entities needed: Ask next question

Design Principles:
- Thin nodes (just call services)
- Async operations
- Stateless (context-aware via state parameter)
- Try/catch in nodes + dedicated error node
"""

import logging
from typing import Dict, Any, Literal, Optional
from datetime import datetime

from langgraph.graph import StateGraph, END
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.graphs.state import SlotFillingState
from src.nlp.intent.classifier import IntentClassifier
from src.services.dialog_state_manager import DialogStateManager
from src.services.question_generator import QuestionGenerator
from src.services.entity_extractor import EntityExtractor
from src.services.entity_validator import EntityValidator
from src.nlp.intent.config import INTENT_CONFIGS, EntityType, IntentType

logger = logging.getLogger(__name__)


# ============================================================
# NODE FUNCTIONS (Thin, Async, Stateless)
# ============================================================

async def classify_intent_node(
    state: SlotFillingState,
    classifier: IntentClassifier,
    dialog_manager: DialogStateManager
) -> Dict[str, Any]:
    """
    Node: Classify user intent (context-aware)
    
    Args:
        state: Current conversation state
        classifier: Intent classifier service
        dialog_manager: Dialog state manager service
        
    Returns:
        Updated state with intent classification result
    """
    try:
        logger.info(f"[classify_intent_node] Processing message: {state['current_message'][:50]}...")

        # Get dialog state from DB
        dialog_state = await dialog_manager.get_active_state(state['session_id'])

        # CRITICAL FIX: When in slot-filling mode, check if user is asking a NEW question
        # vs. providing a follow-up answer
        if dialog_state:
            logger.info(f"[classify_intent_node] Active dialog state detected: {dialog_state.intent}")

            # First, check if this looks like a question (not a short answer)
            message_lower = state['current_message'].lower().strip()

            # Question indicators
            question_words = ['what', 'how', 'why', 'when', 'where', 'which', 'who', 'can you', 'could you',
                            'would you', 'do you', 'does', 'is there', 'are there', 'tell me', 'show me',
                            'explain', 'list', 'give me']
            has_question_mark = '?' in state['current_message']
            starts_with_question = any(message_lower.startswith(qw) for qw in question_words)
            is_likely_question = has_question_mark or starts_with_question

            # Short answers (1-3 words) are likely follow-up responses, not questions
            word_count = len(state['current_message'].split())
            is_short_answer = word_count <= 3

            # Only check for intent change if it looks like a question (not a short answer)
            if is_likely_question and not is_short_answer:
                logger.info(f"[classify_intent_node] Message looks like a question, classifying WITHOUT context to detect intent changes")

                # Classify WITHOUT dialog_state context to get true intent
                intent_result_no_context, classification_method_no_context = await classifier.classify(
                    message=state['current_message'],
                    conversation_history=None,  # No context
                    dialog_state=None  # No dialog state
                )

                confidence_no_context = intent_result_no_context.intents[0].confidence if intent_result_no_context.intents else 0.0
                logger.info(f"[classify_intent_node] No-context classification: {intent_result_no_context.primary_intent}, Confidence: {confidence_no_context}, Method: {classification_method_no_context}")

                # Check if intent is different from dialog_state intent
                if intent_result_no_context.primary_intent != dialog_state.intent:
                    logger.info(f"[classify_intent_node] Intent changed from {dialog_state.intent} to {intent_result_no_context.primary_intent}")
                    logger.info(f"[classify_intent_node] Exiting slot-filling to handle new intent")

                    # Mark as intent changed and exit slot-filling
                    return {
                        "intent_result": intent_result_no_context.model_dump(),
                        "primary_intent": intent_result_no_context.primary_intent,
                        "intent_confidence": confidence_no_context,
                        "classification_method": classification_method_no_context,
                        "collected_entities": state.get('collected_entities', {}),
                        "intent_changed": True,
                        "original_intent": dialog_state.intent,
                        "metadata": {
                            **state.get("metadata", {}),
                            "nodes_executed": state.get("metadata", {}).get("nodes_executed", []) + ["classify_intent_node"]
                        }
                    }
                else:
                    logger.info(f"[classify_intent_node] Question detected but intent unchanged ({dialog_state.intent}), continuing with slot-filling")
                    # Use the no-context result since intent is the same
                    intent_result = intent_result_no_context
                    classification_method = classification_method_no_context
                    confidence = confidence_no_context
            else:
                logger.info(f"[classify_intent_node] Message looks like a follow-up answer (short or not a question), continuing with slot-filling")
                # For short answers, do context-aware classification to extract entities
                intent_result, classification_method = await classifier.classify(
                    message=state['current_message'],
                    conversation_history=state.get('conversation_history'),
                    dialog_state=dialog_state
                )
                confidence = intent_result.intents[0].confidence if intent_result.intents else 0.0

            # Intent is the same, continue with slot-filling
            logger.info(f"[classify_intent_node] Intent unchanged ({dialog_state.intent}), continuing with context-aware classification")
            intent_changed = False
        else:
            # No dialog state, normal classification
            intent_result, classification_method = await classifier.classify(
                message=state['current_message'],
                conversation_history=state.get('conversation_history'),
                dialog_state=None
            )

            confidence = intent_result.intents[0].confidence if intent_result.intents else 0.0
            logger.info(f"[classify_intent_node] Intent: {intent_result.primary_intent}, Confidence: {confidence}, Method: {classification_method}")
            intent_changed = False

        # Extract entities from intent result
        intent_entities = intent_result.intents[0].entities if intent_result.intents else {}

        # Normalize intent entities before merging
        # This ensures entities like "30 october" are converted to "2025-10-30"
        from src.utils.entity_normalizer import normalize_date, normalize_time
        normalized_intent_entities = {}
        for key, value in intent_entities.items():
            if key == 'date':
                normalized = normalize_date(value)
                normalized_intent_entities[key] = normalized if normalized else value
            elif key == 'time':
                normalized = normalize_time(value)
                normalized_intent_entities[key] = normalized if normalized else value
            else:
                normalized_intent_entities[key] = value

        if normalized_intent_entities != intent_entities:
            logger.info(f"[classify_intent_node] Normalized entities: {intent_entities} → {normalized_intent_entities}")

        # Merge with existing collected entities
        # IMPORTANT: Preserve existing entities - don't overwrite with new intent entities
        # This prevents losing validated entities when processing follow-up messages
        existing_entities = state.get('collected_entities', {})
        merged_entities = {**normalized_intent_entities, **existing_entities}  # existing_entities takes precedence

        logger.info(f"[classify_intent_node] Existing entities: {existing_entities}, Intent entities: {normalized_intent_entities}, Merged: {merged_entities}")

        # Save newly extracted entities to database
        # This ensures entities extracted by pattern matching or LLM are persisted
        if normalized_intent_entities and dialog_state:
            try:
                from src.schemas.dialog_state import DialogStateUpdate
                await dialog_manager.update_state(
                    session_id=state['session_id'],
                    update_data=DialogStateUpdate(
                        collected_entities=merged_entities
                    )
                )
                logger.info(f"[classify_intent_node] ✅ Saved entities to database: {list(merged_entities.keys())}")
            except Exception as e:
                logger.warning(f"[classify_intent_node] Failed to save entities to database: {e}")

        # Update state
        return {
            "intent_result": intent_result.model_dump(),
            "primary_intent": intent_result.primary_intent,
            "intent_confidence": confidence,
            "classification_method": classification_method,
            "collected_entities": merged_entities,
            "intent_changed": intent_changed,
            "original_intent": dialog_state.intent if dialog_state else None,
            "metadata": {
                **state.get("metadata", {}),
                "nodes_executed": state.get("metadata", {}).get("nodes_executed", []) + ["classify_intent_node"]
            }
        }

    except Exception as e:
        logger.error(f"[classify_intent_node] Error: {e}", exc_info=True)
        return {
            "error": {
                "type": "IntentClassificationError",
                "message": str(e),
                "node": "classify_intent_node"
            }
        }


async def check_follow_up_node(
    state: SlotFillingState,
    dialog_manager: DialogStateManager
) -> Dict[str, Any]:
    """
    Node: Check if current message is a follow-up response
    
    Args:
        state: Current conversation state
        dialog_manager: Dialog state manager service
        
    Returns:
        Updated state with follow-up detection result
    """
    try:
        logger.info(f"[check_follow_up_node] Checking if follow-up...")

        # Check if this is the first message in slot-filling (no last_question_asked)
        last_question = state.get('last_question_asked')
        if not last_question:
            logger.info(f"[check_follow_up_node] First message in slot-filling, not a follow-up")
            return {
                "is_follow_up": False,
                "follow_up_confidence": 0.0,
                "expected_entity": None,
                "metadata": {
                    **state.get("metadata", {}),
                    "nodes_executed": state.get("metadata", {}).get("nodes_executed", []) + ["check_follow_up_node"]
                }
            }

        # Check if follow-up
        follow_up_result = await dialog_manager.is_follow_up_response(
            message=state['current_message'],
            session_id=state['session_id']
        )

        logger.info(f"[check_follow_up_node] Is follow-up: {follow_up_result.is_follow_up}, Confidence: {follow_up_result.confidence}")

        return {
            "is_follow_up": follow_up_result.is_follow_up,
            "follow_up_confidence": follow_up_result.confidence,
            "expected_entity": follow_up_result.expected_entity,
            "metadata": {
                **state.get("metadata", {}),
                "nodes_executed": state.get("metadata", {}).get("nodes_executed", []) + ["check_follow_up_node"]
            }
        }
    
    except Exception as e:
        logger.error(f"[check_follow_up_node] Error: {e}", exc_info=True)
        return {
            "error": {
                "type": "FollowUpDetectionError",
                "message": str(e),
                "node": "check_follow_up_node"
            }
        }


async def extract_initial_entities_node(
    state: SlotFillingState,
    entity_extractor: EntityExtractor
) -> Dict[str, Any]:
    """
    Node: Extract entities from initial message (not a follow-up)
    This handles cases like "i want to book texture pianting" where the service name is in the initial message

    Args:
        state: Current conversation state
        entity_extractor: Entity extractor service

    Returns:
        Updated state with extracted entities
    """
    try:
        logger.info(f"[extract_initial_entities_node] Extracting entities from initial message")

        message = state.get('current_message', '')
        intent = state.get('primary_intent')
        collected_entities = state.get('collected_entities', {})

        # Only try to extract service_type for booking_management intent
        # Re-extract if service_type exists but doesn't have resolved service metadata
        should_extract = (
            intent == "booking_management" and
            ('service_type' not in collected_entities or '_resolved_service' not in collected_entities)
        )

        if should_extract:
            logger.info(f"[extract_initial_entities_node] Attempting to extract service_type from: '{message}'")

            # Try to extract service name using ServiceNameResolver
            context = {
                'intent': intent,
                'session_id': state.get('session_id'),
                'user_id': state.get('user_id')
            }

            extraction_result = await entity_extractor.extract_from_follow_up(
                message=message,
                expected_entity=EntityType.SERVICE_TYPE,
                context=context
            )

            logger.info(f"[extract_initial_entities_node] Extraction result: {extraction_result}")

            if extraction_result and extraction_result.confidence >= 0.7:
                logger.info(f"[extract_initial_entities_node] ✅ Extracted service: {extraction_result.entity_value}")

                # Check if this is a resolved service (has metadata)
                if extraction_result.metadata and '_resolved_service' in extraction_result.metadata:
                    resolved_service = extraction_result.metadata['_resolved_service']
                    logger.info(f"[extract_initial_entities_node] ✅ Service pre-resolved: {resolved_service}")

                    # Check if service has subcategory_id
                    has_subcategory = resolved_service.get('subcategory_id') is not None

                    if has_subcategory:
                        # Service is fully resolved (has both category and subcategory)
                        logger.info(f"[extract_initial_entities_node] Service fully resolved with subcategory")
                        collected_entities['_resolved_service'] = resolved_service

                        # Pre-populate service_type and service_subcategory
                        if resolved_service.get('category_id'):
                            collected_entities['service_type'] = str(resolved_service['category_id'])
                            logger.info(f"[extract_initial_entities_node] Pre-populated service_type: {resolved_service['category_id']}")

                        if resolved_service.get('subcategory_id'):
                            collected_entities['service_subcategory'] = str(resolved_service['subcategory_id'])
                            logger.info(f"[extract_initial_entities_node] Pre-populated service_subcategory: {resolved_service['subcategory_id']}")

                        # Store service name for QuestionGenerator to use in context
                        service_name = resolved_service.get('subcategory_name') or resolved_service.get('service_name') or resolved_service.get('category_name')
                        if service_name:
                            collected_entities['_service_name'] = service_name
                            logger.info(f"[extract_initial_entities_node] Stored service name for context: {service_name}")
                    else:
                        # Service resolved to category only (no subcategory)
                        # Store only category_id, let validation handle subcategory selection
                        logger.info(f"[extract_initial_entities_node] Service resolved to category only (no subcategory), will need subcategory selection")
                        if resolved_service.get('category_id'):
                            collected_entities['service_type'] = str(resolved_service['category_id'])
                            logger.info(f"[extract_initial_entities_node] Extracted service_type (category only): {resolved_service['category_id']}")

                        # Store category name for context
                        category_name = resolved_service.get('category_name')
                        if category_name:
                            collected_entities['_service_name'] = category_name
                            logger.info(f"[extract_initial_entities_node] Stored category name for context: {category_name}")
                elif extraction_result.metadata and 'subcategory_hint' in extraction_result.metadata:
                    # Service extracted with subcategory hint (e.g., "kitchen cleaning" -> category="cleaning", hint="Kitchen Cleaning")
                    subcategory_hint = extraction_result.metadata['subcategory_hint']
                    logger.info(f"[extract_initial_entities_node] ✅ Service extracted with subcategory hint: {subcategory_hint}")

                    # Store category
                    collected_entities['service_type'] = extraction_result.entity_value
                    logger.info(f"[extract_initial_entities_node] Extracted service_type: {extraction_result.entity_value}")

                    # Store subcategory hint for later resolution
                    collected_entities['_subcategory_hint'] = subcategory_hint
                    logger.info(f"[extract_initial_entities_node] Stored subcategory hint: {subcategory_hint}")
                else:
                    # Regular service_type extraction (category only)
                    collected_entities['service_type'] = extraction_result.entity_value
                    logger.info(f"[extract_initial_entities_node] Extracted service_type: {extraction_result.entity_value}")
            else:
                logger.info(f"[extract_initial_entities_node] No service extracted or low confidence")

        return {
            "collected_entities": collected_entities,
            "metadata": {
                **state.get("metadata", {}),
                "nodes_executed": state.get("metadata", {}).get("nodes_executed", []) + ["extract_initial_entities_node"]
            }
        }

    except Exception as e:
        logger.error(f"[extract_initial_entities_node] Error: {e}", exc_info=True)
        # Don't fail the whole flow - just continue without extracted entities
        return {
            "collected_entities": state.get('collected_entities', {}),
            "metadata": {
                **state.get("metadata", {}),
                "nodes_executed": state.get("metadata", {}).get("nodes_executed", []) + ["extract_initial_entities_node"]
            }
        }


async def extract_entity_node(
    state: SlotFillingState,
    entity_extractor: EntityExtractor
) -> Dict[str, Any]:
    """
    Node: Extract entity value from follow-up response

    Args:
        state: Current conversation state
        entity_extractor: Entity extractor service

    Returns:
        Updated state with extracted entity
    """
    try:
        expected_entity = state.get('expected_entity')
        logger.info(f"[extract_entity_node] Extracting entity: {expected_entity}")

        # Check if entity was already extracted by intent classifier
        collected_entities = state.get('collected_entities', {})

        # NEW: Check if service was pre-resolved by ServiceNameResolver
        # This happens when user says "i want to book texture painting" and we resolve it to a specific service
        if expected_entity == 'service_type' and '_resolved_service' in collected_entities:
            resolved_service = collected_entities['_resolved_service']
            logger.info(f"[extract_entity_node] ✅ Service pre-resolved by ServiceNameResolver: {resolved_service}")

            # Pre-populate service_type and service_subcategory
            if resolved_service.get('category_id'):
                collected_entities['service_type'] = str(resolved_service['category_id'])
                logger.info(f"[extract_entity_node] Pre-populated service_type: {resolved_service['category_id']}")

            if resolved_service.get('subcategory_id'):
                collected_entities['service_subcategory'] = str(resolved_service['subcategory_id'])
                logger.info(f"[extract_entity_node] Pre-populated service_subcategory: {resolved_service['subcategory_id']}")

            # Return the category_id as service_type
            return {
                "extracted_entity": {
                    "entity_type": "service_type",
                    "entity_value": str(resolved_service['category_id']),
                    "normalized_value": str(resolved_service['category_id']),
                    "confidence": 0.95,
                    "extraction_method": "service_name_resolver",
                    "metadata": {"_resolved_service": resolved_service}
                },
                "extraction_failed": False,
                "collected_entities": collected_entities,  # Update collected entities
                "metadata": {
                    **state.get("metadata", {}),
                    "nodes_executed": state.get("metadata", {}).get("nodes_executed", []) + ["extract_entity_node"],
                    "service_pre_resolved": True
                }
            }

        # Check if the expected entity was already extracted
        if expected_entity and expected_entity in collected_entities:
            logger.info(f"[extract_entity_node] ✅ Expected entity '{expected_entity}' already extracted by intent classifier: {collected_entities[expected_entity]}")
            # Use the entity extracted by intent classifier
            return {
                "extracted_entity": {
                    "entity_type": expected_entity,
                    "entity_value": collected_entities[expected_entity],
                    "normalized_value": collected_entities[expected_entity],
                    "confidence": 0.95,
                    "extraction_method": "intent_classifier"
                },
                "extraction_failed": False,
                "metadata": {
                    **state.get("metadata", {}),
                    "nodes_executed": state.get("metadata", {}).get("nodes_executed", []) + ["extract_entity_node"]
                }
            }

        # Check if user provided a DIFFERENT entity than what we asked for
        # This happens when user says "day after tomorrow" when we asked for location
        needed_entities = state.get('needed_entities', [])
        for entity_key in collected_entities:
            if entity_key in needed_entities and entity_key != expected_entity:
                logger.info(f"[extract_entity_node] ⚠️  User provided '{entity_key}' instead of expected '{expected_entity}'. Accepting it and will ask for '{expected_entity}' later.")
                # User provided a different entity - accept it and mark extraction as failed
                # so we ask for the expected entity again
                return {
                    "extracted_entity": {
                        "entity_type": entity_key,
                        "entity_value": collected_entities[entity_key],
                        "normalized_value": collected_entities[entity_key],
                        "confidence": 0.95,
                        "extraction_method": "intent_classifier_different"
                    },
                    "extraction_failed": False,  # Entity was extracted, just not the expected one
                    "metadata": {
                        **state.get("metadata", {}),
                        "nodes_executed": state.get("metadata", {}).get("nodes_executed", []) + ["extract_entity_node"],
                        "extracted_different_entity": True
                    }
                }

        # Check if we should try to extract multiple entities
        # This happens when user provides combined input like "tomorrow 4pm"
        # OR for complaints where user might provide both issue_type and description in one message
        needed_entities = state.get('needed_entities', [])
        intent = state.get('primary_intent')
        multiple_needed = len(needed_entities) > 1

        # For complaints, always try to extract multiple entities from detailed messages
        is_complaint_with_details = (
            intent == "complaint" and
            len(state.get('current_message', '').split()) >= 5  # Message has 5+ words
        )

        if multiple_needed or is_complaint_with_details:
            # Try to extract multiple entities from the message
            logger.info(f"[extract_entity_node] Trying to extract multiple entities: {needed_entities}")
            multiple_results = await entity_extractor.extract_multiple_entities(
                message=state['current_message'],
                expected_entities=[EntityType(e) for e in needed_entities],
                context={
                    "collected_entities": collected_entities,
                    "last_question": state.get('last_question_asked'),
                    "user_id": state['user_id']
                }
            )

            # If we found multiple entities, return the expected one but store all
            if multiple_results:
                logger.info(f"[extract_entity_node] Found multiple entities: {list(multiple_results.keys())}")

                # Store all extracted entities for later processing
                state_update = {
                    "multiple_entities_extracted": multiple_results,
                    "metadata": {
                        **state.get("metadata", {}),
                        "nodes_executed": state.get("metadata", {}).get("nodes_executed", []) + ["extract_entity_node"],
                        "multiple_extraction": True
                    }
                }

                # Return the expected entity if found
                if expected_entity in multiple_results:
                    state_update["extracted_entity"] = multiple_results[expected_entity].model_dump()
                    return state_update
                else:
                    # Return the first entity found
                    first_entity = next(iter(multiple_results.values()))
                    state_update["extracted_entity"] = first_entity.model_dump()
                    return state_update

        # Extract single entity from message (original logic)
        # Build context for extraction
        extraction_context = {
            "collected_entities": collected_entities,
            "last_question": state.get('last_question_asked'),
            "user_id": state['user_id']
        }

        # For service_subcategory extraction, add available subcategories from metadata
        if expected_entity == 'service_subcategory':
            metadata = state.get('metadata', {})
            available_subcategories = metadata.get('available_subcategories', [])
            if available_subcategories:
                extraction_context['available_subcategories'] = available_subcategories
                logger.info(f"[extract_entity_node] Added {len(available_subcategories)} available subcategories to extraction context")

        extraction_result = await entity_extractor.extract_from_follow_up(
            message=state['current_message'],
            expected_entity=EntityType(expected_entity),
            context=extraction_context
        )
        
        if extraction_result:
            logger.info(f"[extract_entity_node] Extracted: {extraction_result.entity_type} = {extraction_result.entity_value}")

            return {
                "extracted_entity": extraction_result.model_dump(),
                "metadata": {
                    **state.get("metadata", {}),
                    "nodes_executed": state.get("metadata", {}).get("nodes_executed", []) + ["extract_entity_node"]
                }
            }
        else:
            # Entity not found in message - this is NOT an error, just means we need to ask for it
            logger.info(f"[extract_entity_node] Entity not found in message, will ask for it")
            return {
                "extraction_failed": True,
                "metadata": {
                    **state.get("metadata", {}),
                    "nodes_executed": state.get("metadata", {}).get("nodes_executed", []) + ["extract_entity_node"]
                }
            }
    
    except Exception as e:
        logger.error(f"[extract_entity_node] Error: {e}", exc_info=True)
        return {
            "error": {
                "type": "EntityExtractionError",
                "message": str(e),
                "node": "extract_entity_node"
            }
        }


async def validate_entity_node(
    state: SlotFillingState,
    entity_validator: EntityValidator
) -> Dict[str, Any]:
    """
    Node: Validate extracted entity value OR collected entity that needs validation

    Args:
        state: Current conversation state
        entity_validator: Entity validator service

    Returns:
        Updated state with validation result
    """
    try:
        logger.info(f"[validate_entity_node] Validating entity...")

        extracted = state.get('extracted_entity', {})
        collected_entities = state.get('collected_entities', {})

        # Check if we have an extracted entity (normal flow)
        if extracted and 'entity_type' in extracted:
            logger.info(f"[validate_entity_node] Validating extracted entity: {extracted['entity_type']}={extracted.get('entity_value')}")
            entity_type = extracted['entity_type']
            entity_value = extracted.get('normalized_value') or extracted['entity_value']

            # Check if extracted entity has subcategory hint metadata
            if entity_type == 'service_type' and extracted.get('metadata') and 'subcategory_hint' in extracted.get('metadata', {}):
                subcategory_hint = extracted['metadata']['subcategory_hint']
                logger.info(f"[validate_entity_node] ✅ Found subcategory hint in extracted entity: {subcategory_hint}")
                # Store subcategory hint in collected_entities for later use
                collected_entities['_subcategory_hint'] = subcategory_hint

        # NEW: Check if we need to validate a collected service_type (subcategory validation flow)
        elif 'service_type' in collected_entities:
            logger.info(f"[validate_entity_node] Validating collected service_type: {collected_entities['service_type']}")
            entity_type = 'service_type'
            entity_value = collected_entities['service_type']

            # Create a mock extracted entity for consistency
            extracted = {
                'entity_type': 'service_type',
                'entity_value': entity_value,
                'normalized_value': entity_value
            }

        else:
            logger.warning(f"[validate_entity_node] No entity to validate, skipping validation")
            return {
                "validation_result": {
                    "is_valid": False,
                    "error_message": "Could not find entity to validate"
                },
                "metadata": {
                    **state.get("metadata", {}),
                    "validation_skipped": True
                }
            }

        # Validate entity
        validation_result = await entity_validator.validate(
            entity_type=EntityType(entity_type),
            value=entity_value,
            context={
                "user_id": state['user_id'],
                "collected_entities": collected_entities
            }
        )

        logger.info(f"[validate_entity_node] Valid: {validation_result.is_valid}")

        # Handle subcategory validation failure
        result = {
            "validation_result": validation_result.model_dump(),
            "extracted_entity": extracted,  # Ensure extracted_entity is available for downstream nodes
            "collected_entities": collected_entities,  # Include updated collected_entities (may have subcategory hint)
            "metadata": {
                **state.get("metadata", {}),
                "nodes_executed": state.get("metadata", {}).get("nodes_executed", []) + ["validate_entity_node"]
            }
        }

        # If service_type validation failed due to subcategory requirement
        if not validation_result.is_valid and entity_type == 'service_type':
            metadata = validation_result.metadata or {}
            if metadata.get('requires_subcategory_selection', False):
                logger.info(f"[validate_entity_node] Service requires subcategory selection, checking if already collected...")

                # Check if service_subcategory is already collected (pre-resolved by ServiceNameResolver)
                if 'service_subcategory' in collected_entities:
                    logger.info(f"[validate_entity_node] ✅ service_subcategory already collected (pre-resolved), skipping subcategory selection")
                    # Mark validation as successful since subcategory is already resolved
                    result['validation_result'] = {
                        "is_valid": True,
                        "normalized_value": entity_value,
                        "metadata": {
                            "requires_subcategory_selection": False,
                            "subcategory_pre_resolved": True
                        }
                    }
                # Check if we have a subcategory hint from extraction
                elif '_subcategory_hint' in collected_entities:
                    subcategory_hint = collected_entities['_subcategory_hint']
                    logger.info(f"[validate_entity_node] ✅ Found subcategory hint: {subcategory_hint}, resolving to subcategory ID...")

                    # Resolve subcategory hint to subcategory ID
                    available_subcategories = metadata.get('available_subcategories', [])
                    logger.info(f"[validate_entity_node] Available subcategories: {[s.get('name') for s in available_subcategories]}")

                    subcategory_id = None
                    subcategory_hint_lower = subcategory_hint.lower().strip()

                    for subcat in available_subcategories:
                        subcat_name = subcat.get('name', '').lower().strip()
                        # Try exact match first
                        if subcat_name == subcategory_hint_lower:
                            subcategory_id = subcat.get('id')
                            logger.info(f"[validate_entity_node] ✅ Exact match: Resolved '{subcategory_hint}' to ID: {subcategory_id}")
                            break
                        # Try partial match (e.g., "Kitchen Cleaning" matches "kitchen cleaning")
                        if subcategory_hint_lower in subcat_name or subcat_name in subcategory_hint_lower:
                            subcategory_id = subcat.get('id')
                            logger.info(f"[validate_entity_node] ✅ Partial match: Resolved '{subcategory_hint}' to '{subcat.get('name')}' (ID: {subcategory_id})")
                            break

                    if subcategory_id:
                        # Store subcategory ID in collected_entities
                        collected_entities['service_subcategory'] = str(subcategory_id)
                        result['collected_entities'] = collected_entities

                        # Mark validation as successful
                        result['validation_result'] = {
                            "is_valid": True,
                            "normalized_value": entity_value,
                            "metadata": {
                                "requires_subcategory_selection": False,
                                "subcategory_resolved_from_hint": True,
                                "subcategory_id": subcategory_id
                            }
                        }
                        logger.info(f"[validate_entity_node] ✅ Subcategory resolved from hint, skipping subcategory selection")
                    else:
                        logger.warning(f"[validate_entity_node] ⚠️ Could not resolve subcategory hint '{subcategory_hint}' to ID. Available: {[s.get('name') for s in available_subcategories]}")
                        # Fall through to normal subcategory selection
                else:
                    # Add service_subcategory to needed entities (at the beginning)
                    current_needed = state.get('needed_entities', [])
                    if 'service_subcategory' not in current_needed:
                        updated_needed = ['service_subcategory'] + current_needed
                        result['needed_entities'] = updated_needed
                        logger.info(f"[validate_entity_node] Updated needed_entities: {updated_needed}")

                    # Add validation error for question generation
                    error_message = validation_result.error_message or "Please specify the service type"
                    result['validation_errors'] = state.get('validation_errors', []) + [error_message]

                    # Add subcategory metadata for question generation
                    result['metadata'].update({
                        'available_subcategories': metadata.get('available_subcategories', []),
                        'service_type': entity_value,
                        'requires_subcategory_selection': True
                    })

                    logger.info(f"[validate_entity_node] Added subcategory metadata: available={metadata.get('available_subcategories', [])}")

        return result

    except Exception as e:
        logger.error(f"[validate_entity_node] Error: {e}", exc_info=True)
        return {
            "error": {
                "type": "EntityValidationError",
                "message": str(e),
                "node": "validate_entity_node"
            }
        }


async def update_dialog_state_node(
    state: SlotFillingState,
    dialog_manager: DialogStateManager
) -> Dict[str, Any]:
    """
    Node: Update dialog state with validated entity
    
    Args:
        state: Current conversation state
        dialog_manager: Dialog state manager service
        
    Returns:
        Updated state with new collected entities
    """
    try:
        logger.info(f"[update_dialog_state_node] Updating dialog state...")
        
        validation_result = state.get('validation_result', {})
        extracted = state.get('extracted_entity', {})
        multiple_extracted = state.get('multiple_entities_extracted', {})
        validation_result = validation_result or {}

        if validation_result.get('is_valid'):
            # Add entity to collected entities
            entity_type = extracted.get('entity_type', '')
            entity_value = validation_result.get('normalized_value', '')

            # Update in-memory state first
            collected = state.get('collected_entities', {}).copy()
            collected[entity_type] = entity_value

            # NEW: Check for resolved service metadata from ServiceNameResolver
            extraction_metadata = extracted.get('metadata', {})
            if extraction_metadata and '_resolved_service' in extraction_metadata:
                resolved_service = extraction_metadata['_resolved_service']
                collected['_resolved_service'] = resolved_service
                logger.info(f"[update_dialog_state_node] ✅ Stored _resolved_service: {resolved_service}")

                # Also store rate_card_id for booking creation
                if resolved_service.get('rate_card_id'):
                    collected['_metadata_rate_card_id'] = resolved_service['rate_card_id']
                    logger.info(f"[update_dialog_state_node] ✅ Stored _metadata_rate_card_id from resolved service: {resolved_service['rate_card_id']}")

            # Store validation metadata (e.g., rate_card_id for service_subcategory)
            validation_metadata = validation_result.get('metadata', {})
            logger.info(f"[update_dialog_state_node] Validation metadata: {validation_metadata}")
            if validation_metadata:
                # Store rate_card_id if present (needed for booking creation)
                if 'rate_card_id' in validation_metadata:
                    collected['_metadata_rate_card_id'] = validation_metadata['rate_card_id']
                    logger.info(f"[update_dialog_state_node] ✅ Stored _metadata_rate_card_id: {validation_metadata['rate_card_id']}")
                else:
                    logger.warning(f"[update_dialog_state_node] ⚠️ No rate_card_id in validation metadata")

                # Store other metadata fields if needed
                if 'service_type' in validation_metadata:
                    collected['_metadata_service_type'] = validation_metadata['service_type']
            else:
                logger.warning(f"[update_dialog_state_node] ⚠️ No validation metadata found")

            # If we extracted multiple entities, add them all (if they're valid)
            if multiple_extracted:
                logger.info(f"[update_dialog_state_node] Processing multiple extracted entities: {list(multiple_extracted.keys())}")
                for entity_key, entity_result in multiple_extracted.items():
                    if entity_key != entity_type:  # Don't duplicate the main entity
                        # For now, assume other entities are valid (we can add validation later)
                        collected[entity_key] = entity_result.normalized_value or entity_result.entity_value
                        logger.info(f"[update_dialog_state_node] Added additional entity: {entity_key} = {collected[entity_key]}")

            needed = [e for e in state.get('needed_entities', []) if e not in collected]

            # Save ALL collected entities to database (not just the new one)
            # This ensures that entities from previous turns are not lost
            from src.schemas.dialog_state import DialogStateUpdate

            logger.info(f"[update_dialog_state_node] 💾 Saving to database - collected_entities: {collected}")

            await dialog_manager.update_state(
                session_id=state['session_id'],
                update_data=DialogStateUpdate(
                    collected_entities=collected,  # Save ALL entities including _metadata_*
                    needed_entities=needed
                )
            )

            logger.info(f"[update_dialog_state_node] Added {entity_type}={entity_value}, All collected: {list(collected.keys())}, Remaining: {needed}")
            
            return {
                "collected_entities": collected,
                "needed_entities": needed,
                "validation_errors": [],
                "metadata": {
                    **state.get("metadata", {}),
                    "nodes_executed": state.get("metadata", {}).get("nodes_executed", []) + ["update_dialog_state_node"]
                }
            }
        else:
            # Validation failed
            error_msg = validation_result.get('error_message', 'Invalid value')
            logger.warning(f"[update_dialog_state_node] Validation failed: {error_msg}")

            # Special handling for service type that requires subcategory selection
            entity_type = extracted.get('entity_type')
            validation_metadata = validation_result.get('metadata', {})

            if (entity_type == 'service_type' and
                validation_metadata.get('requires_subcategory_selection')):

                logger.info(f"[update_dialog_state_node] Service type requires subcategory selection")

                # Store the service type and available subcategories for question generation
                collected = state.get('collected_entities', {}).copy()
                collected['service_type'] = validation_metadata.get('normalized_service_type')

                # Add service_subcategory to needed entities
                needed = state.get('needed_entities', []).copy()
                if 'service_subcategory' not in needed:
                    needed.insert(0, 'service_subcategory')  # Insert at beginning for immediate handling

                # Save state with service type and subcategory requirement
                from src.schemas.dialog_state import DialogStateUpdate
                from src.core.models.dialog_state import DialogStateType
                await dialog_manager.update_state(
                    session_id=state['session_id'],
                    update_data=DialogStateUpdate(
                        # Provide required fields for the DialogStateUpdate model
                        state=DialogStateType.COLLECTING_INFO,
                        intent=state.get('primary_intent'),
                        pending_action=None,
                        expires_in_hours=24,
                        collected_entities=collected,
                        needed_entities=needed,
                        context={
                            "available_subcategories": validation_metadata.get('available_subcategories', []),
                            "service_type": validation_metadata.get('normalized_service_type')
                        }
                    )
                )

                logger.info(f"[update_dialog_state_node] Added service_subcategory to needed entities: {needed}")

                return {
                    "collected_entities": collected,
                    "needed_entities": needed,
                    "validation_errors": [error_msg],
                    "question_attempt_count": state.get('question_attempt_count', 0) + 1,
                    "metadata": {
                        **state.get("metadata", {}),
                        "available_subcategories": validation_metadata.get('available_subcategories', []),
                        "service_type": validation_metadata.get('normalized_service_type'),
                        "nodes_executed": state.get("metadata", {}).get("nodes_executed", []) + ["update_dialog_state_node"]
                    }
                }

            return {
                "validation_errors": state.get('validation_errors', []) + [error_msg],
                "question_attempt_count": state.get('question_attempt_count', 0) + 1
            }
    
    except Exception as e:
        logger.error(f"[update_dialog_state_node] Error: {e}", exc_info=True)
        return {
            "error": {
                "type": "DialogStateUpdateError",
                "message": str(e),
                "node": "update_dialog_state_node"
            }
        }


async def determine_needed_entities_node(
    state: SlotFillingState,
    db: Optional[AsyncSession] = None
) -> Dict[str, Any]:
    """
    Node: Determine which entities are still needed

    Args:
        state: Current conversation state
        db: Database session (optional, for checking existing addresses)

    Returns:
        Updated state with needed entities list
    """
    try:
        logger.info(f"[determine_needed_entities_node] Determining needed entities...")

        intent = state.get('primary_intent')
        collected = state.get('collected_entities', {})

        # Get required entities for this intent
        # Convert string intent to IntentType enum if needed
        intent_enum = IntentType(intent) if isinstance(intent, str) else intent
        intent_config = INTENT_CONFIGS.get(intent_enum) if intent_enum else None  # type: ignore
        if not intent_config:
            logger.warning(f"[determine_needed_entities_node] No config for intent: {intent} (enum: {intent_enum})")
            return {"needed_entities": []}

        # Determine needed entities based on action (for booking_management)
        required_entities = [e.value for e in intent_config.required_entities]

        # Special handling for booking_management
        if intent == "booking_management":
            action = collected.get("action", "")

            if action == "book":
                # For booking, we need: service_type, location, date, time
                # Order matters: location first (to check availability), then date/time
                required_entities = ["service_type", "location", "date", "time"]

        # Special handling for complaint - ensure correct order
        elif intent == "complaint":
            # Order matters: issue_type first, then booking_id (to validate), then description
            required_entities = ["issue_type", "booking_id", "description"]

        # Filter out already collected entities
        needed = [e for e in required_entities if e not in collected]

        # DEBUG: Log the calculation
        logger.info(f"[determine_needed_entities_node] 🔍 DEBUG - Intent: {intent} (enum: {intent_enum})")
        logger.info(f"[determine_needed_entities_node] 🔍 DEBUG - Intent config found: {intent_config is not None}")
        logger.info(f"[determine_needed_entities_node] 🔍 DEBUG - Required entities: {required_entities}")
        logger.info(f"[determine_needed_entities_node] 🔍 DEBUG - Collected entities: {list(collected.keys())}")
        logger.info(f"[determine_needed_entities_node] 🔍 DEBUG - Needed entities: {needed}")

        # NEW: If service was pre-resolved by ServiceNameResolver, skip service_subcategory
        if '_resolved_service' in collected and 'service_subcategory' in collected:
            logger.info(f"[determine_needed_entities_node] Service pre-resolved, service_subcategory already set")
            # service_subcategory is already in collected, so it will be filtered out above

        # CRITICAL: Check if service_type requires subcategory selection
        # This must happen BEFORE we proceed to generate questions
        if intent == "booking_management" and 'service_type' in collected and 'service_subcategory' not in collected:
            service_type = collected.get('service_type', '')
            logger.info(f"[determine_needed_entities_node] Checking if service_type='{service_type}' requires subcategory selection")

            # Map category IDs to service names
            category_id_to_service = {
                "1": "home_cleaning",
                "13": "ac",
                "2": "appliance_repair",
                "3": "plumbing",
                "4": "electrical",
                "5": "carpentry",
                "6": "painting",
                "7": "pest_control",
                "8": "water_purifier",
                "9": "car_care",
                "10": "salon_for_women",
                "11": "salon_for_men",
                "12": "packers_and_movers"
            }

            # Convert category ID to service name if needed
            normalized_service = category_id_to_service.get(service_type, service_type.lower())

            # Services that require subcategory selection
            services_requiring_subcategory = {
                "home_cleaning", "appliance_repair", "plumbing", "electrical",
                "carpentry", "painting", "pest_control", "water_purifier",
                "car_care", "salon_for_women", "salon_for_men", "packers_and_movers"
            }

            if normalized_service in services_requiring_subcategory:
                # Add service_subcategory to the FRONT of needed entities (highest priority)
                if 'service_subcategory' not in needed:
                    needed.insert(0, 'service_subcategory')
                    logger.info(f"[determine_needed_entities_node] ✅ Service '{normalized_service}' requires subcategory selection, added to needed entities")
                    logger.info(f"[determine_needed_entities_node] Updated needed entities: {needed}")
            else:
                logger.info(f"[determine_needed_entities_node] Service '{normalized_service}' does NOT require subcategory selection")

        # Special check: If location is needed for booking, check if user has existing addresses
        logger.info(f"[determine_needed_entities_node] Checking auto-fill conditions: location_needed={'location' in needed}, intent={intent}, action={collected.get('action')}, db={db is not None}")

        if "location" in needed and intent == "booking_management" and collected.get("action") == "book" and db:
            # Check if user has any saved addresses
            from src.core.models import Address
            user_id = state.get('user_id')
            session_id = state.get('session_id')
            logger.info(f"[determine_needed_entities_node] Checking addresses for user_id: {user_id}")

            if user_id:
                try:
                    # Check for default address first, then any address
                    address_result = await db.execute(
                        select(Address)
                        .where(Address.user_id == user_id)
                        .order_by(Address.is_default.desc(), Address.created_at.desc())
                        .limit(1)
                    )
                    existing_address = address_result.scalar_one_or_none()
                    logger.info(f"[determine_needed_entities_node] Found existing address: {existing_address is not None}")

                    if existing_address:
                        # User has an existing address - auto-fill location
                        # Format: "address_line1, city, state, pincode"
                        auto_location = f"{existing_address.address_line1}, {existing_address.city}, {existing_address.state}, {existing_address.pincode}"
                        collected['location'] = auto_location
                        needed.remove('location')
                        logger.info(f"[determine_needed_entities_node] ✅ Auto-filled location from existing address: {auto_location}")

                        # IMPORTANT: Save the auto-filled location to database immediately
                        # This ensures it persists across turns
                        if session_id:
                            try:
                                from src.services.dialog_state_manager import DialogStateManager
                                from src.schemas.dialog_state import DialogStateUpdate
                                dialog_manager = DialogStateManager(db)
                                await dialog_manager.update_state(
                                    session_id=session_id,
                                    update_data=DialogStateUpdate(
                                        collected_entities=collected
                                    )
                                )
                                logger.info(f"[determine_needed_entities_node] ✅ Saved auto-filled location to database")
                            except Exception as save_error:
                                logger.warning(f"[determine_needed_entities_node] Failed to save auto-filled location: {save_error}")
                    else:
                        logger.info(f"[determine_needed_entities_node] No existing address found for user {user_id}")
                except Exception as e:
                    logger.warning(f"[determine_needed_entities_node] Error checking existing addresses: {e}")
                    import traceback
                    logger.warning(f"[determine_needed_entities_node] Traceback: {traceback.format_exc()}")
                    # Continue without auto-fill - will ask user for location
            else:
                logger.warning(f"[determine_needed_entities_node] No user_id in state")

        logger.info(f"[determine_needed_entities_node] Required: {required_entities}, Collected: {list(collected.keys())}, Needed: {needed}")

        return {
            "needed_entities": needed,
            "collected_entities": collected,  # Return updated collected entities (includes auto-filled location)
            "metadata": {
                **state.get("metadata", {}),
                "nodes_executed": state.get("metadata", {}).get("nodes_executed", []) + ["determine_needed_entities_node"]
            }
        }

    except Exception as e:
        logger.error(f"[determine_needed_entities_node] Error: {e}", exc_info=True)
        return {
            "error": {
                "type": "DetermineEntitiesError",
                "message": str(e),
                "node": "determine_needed_entities_node"
            }
        }


async def generate_question_node(
    state: SlotFillingState,
    question_generator: QuestionGenerator,
    dialog_manager: DialogStateManager
) -> Dict[str, Any]:
    """
    Node: Generate question for next missing entity

    Args:
        state: Current conversation state
        question_generator: Question generator service
        dialog_manager: Dialog state manager

    Returns:
        Updated state with generated question
    """
    try:
        logger.info(f"[generate_question_node] Generating question...")

        needed = state.get('needed_entities', [])

        if not needed:
            logger.info(f"[generate_question_node] No entities needed, generating confirmation")
            # All entities collected, generate confirmation
            primary_intent = state.get('primary_intent')
            if not primary_intent:
                logger.error("[generate_question_node] No primary_intent found in state")
                return {
                    "error": {"type": "MissingIntent", "message": "No primary intent found", "node": "generate_question_node"},
                    "final_response": "I'm sorry, I couldn't determine what you're trying to do. Could you please rephrase?",
                    "response_type": "error"
                }

            intent_enum = IntentType(primary_intent) if isinstance(primary_intent, str) else primary_intent

            confirmation = question_generator.generate_confirmation(
                intent=intent_enum,
                collected_entities=state.get('collected_entities', {})
            )

            # Save dialog state with awaiting_confirmation status
            try:
                from src.schemas.dialog_state import DialogStateUpdate
                from src.core.models.dialog_state import DialogStateType

                logger.info(f"[generate_question_node] 🔄 Updating dialog state to AWAITING_CONFIRMATION for session {state['session_id']}")

                # Prepare pending action with collected entities for agent execution
                intent_config = INTENT_CONFIGS.get(intent_enum)
                agent_name = intent_config.agent if intent_config else "unknown"

                pending_action = {
                    "action_type": "execute_agent",
                    "intent": primary_intent,
                    "collected_entities": state.get('collected_entities', {}),
                    "agent": agent_name
                }

                await dialog_manager.update_state(
                    session_id=state['session_id'],
                    update_data=DialogStateUpdate(
                        state=DialogStateType.AWAITING_CONFIRMATION,
                        pending_action=pending_action,
                        context={"last_question": confirmation, "awaiting_confirmation": True}
                    )
                )

                # Verify the update
                updated_state = await dialog_manager.get_active_state(state['session_id'])
                if updated_state:
                    logger.info(f"[generate_question_node] ✅ Verified dialog state: state={updated_state.state.value}, context={updated_state.context}")
                else:
                    logger.error(f"[generate_question_node] ❌ Failed to verify dialog state - state not found!")

            except Exception as e:
                logger.error(f"[generate_question_node] ❌ Failed to save awaiting_confirmation state: {e}", exc_info=True)

            return {
                "confirmation_message": confirmation,
                "current_question": confirmation,
                "final_response": confirmation,
                "response_type": "confirmation",
                "dialog_state_type": "awaiting_confirmation",
                "metadata": {
                    **state.get("metadata", {}),
                    "nodes_executed": state.get("metadata", {}).get("nodes_executed", []) + ["generate_question_node"]
                }
            }

        # Get first needed entity
        next_entity = needed[0]

        # Check if we have validation errors (need to re-ask)
        validation_errors = state.get('validation_errors', [])
        if validation_errors:
            error_msg = validation_errors[-1]
            question = f"Sorry, {error_msg}. Please try again: "

            # Add the original question
            primary_intent = state.get('primary_intent')
            if not primary_intent:
                logger.error("[generate_question_node] No primary_intent found in state")
                return {
                    "error": {"type": "MissingIntent", "message": "No primary intent found", "node": "generate_question_node"},
                    "final_response": "I'm sorry, I couldn't determine what you're trying to do. Could you please rephrase?",
                    "response_type": "error"
                }

            intent_enum = IntentType(primary_intent) if isinstance(primary_intent, str) else primary_intent

            # Build context for question generation
            context = {}
            if next_entity == 'service_subcategory':
                # Pass available subcategories for service subcategory questions
                context['available_subcategories'] = state.get('metadata', {}).get('available_subcategories', [])
                context['service_type'] = state.get('metadata', {}).get('service_type', '')

            original_question = question_generator.generate(
                entity_type=EntityType(next_entity),
                intent=intent_enum,
                collected_entities=state.get('collected_entities', {}),
                context=context
            )
            question += original_question
        else:
            # Generate new question
            primary_intent = state.get('primary_intent')
            if not primary_intent:
                logger.error("[generate_question_node] No primary_intent found in state")
                return {
                    "error": {"type": "MissingIntent", "message": "No primary intent found", "node": "generate_question_node"},
                    "final_response": "I'm sorry, I couldn't determine what you're trying to do. Could you please rephrase?",
                    "response_type": "error"
                }

            intent_enum = IntentType(primary_intent) if isinstance(primary_intent, str) else primary_intent

            # Build context for question generation
            context = {}
            if next_entity == 'service_subcategory':
                # Pass available subcategories for service subcategory questions
                context['available_subcategories'] = state.get('metadata', {}).get('available_subcategories', [])
                context['service_type'] = state.get('metadata', {}).get('service_type', '')

            question = question_generator.generate(
                entity_type=EntityType(next_entity),
                intent=intent_enum,
                collected_entities=state.get('collected_entities', {}),
                context=context
            )

        logger.info(f"[generate_question_node] Question: {question[:100]}...")

        # Save last_question_asked and needed_entities to dialog state context for follow-up detection
        try:
            from src.schemas.dialog_state import DialogStateUpdate

            # Prepare context update with needed_entities
            context_update = {
                "last_question": question,
                "expected_entity": next_entity,
                "needed_entities": needed  # Save needed_entities to persist across messages
            }

            await dialog_manager.update_state(
                session_id=state['session_id'],
                update_data=DialogStateUpdate(
                    context=context_update
                )
            )
            logger.info(f"[generate_question_node] ✅ Saved last_question and needed_entities to dialog state context")
        except Exception as e:
            logger.warning(f"[generate_question_node] Failed to save last_question to dialog state: {e}")

        return {
            "current_question": question,
            "last_question_asked": question,
            "final_response": question,
            "response_type": "question",
            "dialog_state_type": "collecting_info",
            "expected_entity": next_entity,
            "metadata": {
                **state.get("metadata", {}),
                "nodes_executed": state.get("metadata", {}).get("nodes_executed", []) + ["generate_question_node"]
            }
        }

    except Exception as e:
        logger.error(f"[generate_question_node] Error: {e}", exc_info=True)
        return {
            "error": {
                "type": "QuestionGenerationError",
                "message": str(e),
                "node": "generate_question_node"
            }
        }


async def handle_error_node(
    state: SlotFillingState
) -> Dict[str, Any]:
    """
    Node: Handle errors gracefully

    Args:
        state: Current conversation state

    Returns:
        Updated state with user-friendly error message
    """
    try:
        logger.info(f"[handle_error_node] Handling error...")

        error = state.get('error') or {}
        error_type = error.get('type', 'UnknownError')
        error_message = error.get('message', 'Something went wrong')

        # Generate user-friendly error message
        if error_type == "IntentClassificationError":
            response = "I'm having trouble understanding your request. Could you please rephrase it?"
        elif error_type == "EntityExtractionError":
            response = "I couldn't understand that. Could you please provide the information again?"
        elif error_type == "EntityValidationError":
            response = f"There was an issue with the information provided: {error_message}"
        else:
            response = "I encountered an error. Please try again or contact support if the issue persists."

        logger.info(f"[handle_error_node] Error response: {response}")

        return {
            "final_response": response,
            "response_type": "error",
            "should_end": True,
            "metadata": {
                **state.get("metadata", {}),
                "nodes_executed": state.get("metadata", {}).get("nodes_executed", []) + ["handle_error_node"],
                "error_handled": True
            }
        }

    except Exception as e:
        logger.error(f"[handle_error_node] Error in error handler: {e}", exc_info=True)
        return {
            "final_response": "I encountered an unexpected error. Please try again.",
            "should_end": True
        }


# ============================================================
# CONDITIONAL EDGE FUNCTIONS
# ============================================================

def should_route_to_error(state: SlotFillingState) -> Literal["error", "continue"]:
    """Check if we should route to error handler"""
    if state.get('error'):
        return "error"
    return "continue"


def is_follow_up_response(state: SlotFillingState) -> Literal["follow_up", "new_intent"]:
    """Check if current message is a follow-up response"""
    follow_up_confidence = state.get('follow_up_confidence', 0)
    if state.get('is_follow_up', False) and (follow_up_confidence or 0) > 0.6:
        return "follow_up"
    return "new_intent"


def are_all_entities_collected(state: SlotFillingState) -> Literal["all_collected", "more_needed"]:
    """Check if all required entities are collected"""
    needed = state.get('needed_entities', [])
    if not needed:
        return "all_collected"
    return "more_needed"


def is_validation_successful(state: SlotFillingState) -> Literal["valid", "invalid"]:
    """Check if entity validation was successful"""
    validation_result = state.get('validation_result') or {}
    if validation_result.get('is_valid', False):
        return "valid"
    return "invalid"


def should_trigger_agent_execution(state: SlotFillingState) -> Literal["execute_agent", "ask_question"]:
    """Check if we should trigger agent execution or ask another question"""
    # Check if awaiting confirmation
    if state.get('dialog_state_type') == 'awaiting_confirmation':
        # Check if user confirmed
        message_lower = state.get('current_message', '').lower().strip()
        if message_lower in ["yes", "yeah", "yep", "sure", "ok", "okay", "correct", "right"]:
            return "execute_agent"

    # Check if all entities collected
    needed = state.get('needed_entities', [])
    if not needed:
        return "execute_agent"

    return "ask_question"


# ============================================================
# GRAPH BUILDER
# ============================================================

def create_slot_filling_graph(
    db: AsyncSession,
    classifier: IntentClassifier,
    dialog_manager: DialogStateManager,
    question_generator: QuestionGenerator,
    entity_extractor: EntityExtractor,
    entity_validator: EntityValidator
):
    """
    Create the Slot-Filling Graph

    Args:
        db: Database session
        classifier: Intent classifier
        dialog_manager: Dialog state manager
        question_generator: Question generator
        entity_extractor: Entity extractor
        entity_validator: Entity validator

    Returns:
        Compiled StateGraph
    """
    # Create graph
    graph = StateGraph(SlotFillingState)

    # Add nodes (with service dependencies injected via async wrappers)
    async def _classify_intent(state):
        return await classify_intent_node(state, classifier, dialog_manager)

    async def _check_follow_up(state):
        return await check_follow_up_node(state, dialog_manager)

    async def _extract_initial_entities(state):
        return await extract_initial_entities_node(state, entity_extractor)

    async def _extract_entity(state):
        return await extract_entity_node(state, entity_extractor)

    async def _validate_entity(state):
        return await validate_entity_node(state, entity_validator)

    async def _update_dialog_state(state):
        return await update_dialog_state_node(state, dialog_manager)

    async def _determine_needed_entities(state):
        return await determine_needed_entities_node(state, db)

    async def _generate_question(state):
        return await generate_question_node(state, question_generator, dialog_manager)

    async def _handle_error(state):
        return await handle_error_node(state)

    graph.add_node("classify_intent", _classify_intent)
    graph.add_node("check_follow_up", _check_follow_up)
    graph.add_node("extract_initial_entities", _extract_initial_entities)
    graph.add_node("extract_entity", _extract_entity)
    graph.add_node("validate_entity", _validate_entity)
    graph.add_node("update_dialog_state", _update_dialog_state)
    graph.add_node("determine_needed_entities", _determine_needed_entities)
    graph.add_node("generate_question", _generate_question)
    graph.add_node("handle_error", _handle_error)

    # Set entry point
    graph.set_entry_point("classify_intent")

    # Add edges
    # classify_intent → check error → check intent_changed → check_follow_up
    def route_after_classify(state: SlotFillingState) -> str:
        """Route after intent classification"""
        if state.get('error'):
            logger.info("[route_after_classify] Routing to: error")
            return "error"
        # CRITICAL: Check if intent changed BEFORE going to check_follow_up
        if state.get('intent_changed', False):
            logger.info("[route_after_classify] Intent changed detected, routing to: END")
            return "intent_changed"
        logger.info("[route_after_classify] Routing to: check_follow_up")
        return "continue"

    graph.add_conditional_edges(
        "classify_intent",
        route_after_classify,
        {
            "error": "handle_error",
            "intent_changed": END,  # Exit immediately if intent changed
            "continue": "check_follow_up"
        }
    )

    # check_follow_up → route based on error or follow-up
    def route_after_follow_up_check(state: SlotFillingState) -> str:
        """Route after follow-up check"""
        logger.info(f"[route_after_follow_up_check] Routing decision - intent_changed: {state.get('intent_changed', False)}, is_follow_up: {state.get('is_follow_up', False)}")

        if state.get('error'):
            logger.info("[route_after_follow_up_check] Routing to: error")
            return "error"
        follow_up_confidence = state.get('follow_up_confidence', 0)
        if state.get('is_follow_up', False) and (follow_up_confidence or 0) > 0.6:
            logger.info("[route_after_follow_up_check] Routing to: follow_up")
            return "follow_up"
        # Check if intent has changed (user is asking a different question)
        if state.get('intent_changed', False):
            logger.info("[route_after_follow_up_check] Routing to: intent_changed (EXIT)")
            return "intent_changed"

        # NEW LOGIC: For new intents, check if we have entities that need validation
        collected_entities = state.get('collected_entities', {})
        logger.info(f"[route_after_follow_up_check] New intent - collected entities: {list(collected_entities.keys())}")

        # Check if we have service_type that might need subcategory validation
        if 'service_type' in collected_entities:
            service_type = collected_entities['service_type']
            logger.info(f"[route_after_follow_up_check] Found service_type='{service_type}', checking if validation needed")

            # Map category IDs to service names for validation check
            category_id_to_service = {
                "1": "home_cleaning",
                "13": "ac",
                "2": "appliance_repair",
                "3": "plumbing",
                "4": "electrical",
                "5": "carpentry",
                "6": "painting",
                "7": "pest_control",
                "8": "water_purifier",
                "9": "car_care",
                "10": "salon_for_women",
                "11": "salon_for_men",
                "12": "packers_and_movers"
            }

            # Convert category ID to service name if needed
            normalized_service_type = category_id_to_service.get(service_type, service_type)
            if service_type != normalized_service_type:
                logger.info(f"[route_after_follow_up_check] Converted category ID '{service_type}' to service name '{normalized_service_type}'")

            # If we don't have _resolved_service metadata, try to extract it first
            # This allows ServiceNameResolver to resolve specific service names like "kitchen cleaning"
            if '_resolved_service' not in collected_entities:
                logger.info(f"[route_after_follow_up_check] No _resolved_service metadata, routing to extract_initial_entities to try service name resolution")
                return "new_intent"

            # Services that require subcategory selection (all multi-option services)
            # Include all possible service name variations for compatibility
            services_requiring_validation = [
                # Cleaning variations
                'cleaning', 'home_cleaning', 'house_cleaning', 'clean',
                # Other services
                'appliance_repair', 'appliance', 'plumbing', 'electrical',
                'carpentry', 'painting', 'pest_control', 'pest', 'water_purifier',
                'car_care', 'car', 'salon_for_women', 'salon_for_men', 'salon',
                'packers_and_movers', 'packers', 'movers'
            ]
            if normalized_service_type in services_requiring_validation:
                logger.info(f"[route_after_follow_up_check] Service '{normalized_service_type}' (original: '{service_type}') requires validation, routing to: validate_collected_entities")
                return "validate_collected_entities"

        logger.info("[route_after_follow_up_check] Routing to: new_intent (extract_initial_entities)")
        return "new_intent"

    graph.add_conditional_edges(
        "check_follow_up",
        route_after_follow_up_check,
        {
            "error": "handle_error",
            "follow_up": "extract_entity",
            "intent_changed": END,  # Exit slot-filling, let coordinator handle new intent
            "validate_collected_entities": "validate_entity",  # NEW: Validate collected entities that need subcategory selection
            "new_intent": "extract_initial_entities"  # NEW: Extract entities from initial message before determining needed entities
        }
    )

    # extract_initial_entities → determine_needed_entities
    # This node extracts entities from the initial message (e.g., "i want to book texture pianting")
    # Then we determine what entities are still needed
    graph.add_edge("extract_initial_entities", "determine_needed_entities")

    # extract_entity → check if extraction failed or succeeded
    def route_after_extraction(state: SlotFillingState) -> str:
        """Route after entity extraction"""
        if state.get('error'):
            return "error"
        if state.get('extraction_failed'):
            return "ask_again"
        return "validate"

    graph.add_conditional_edges(
        "extract_entity",
        route_after_extraction,
        {
            "error": "handle_error",
            "ask_again": "generate_question",  # Entity not found, ask again
            "validate": "validate_entity"
        }
    )

    # validate_entity → route based on error or validation result
    def route_after_validation(state: SlotFillingState) -> str:
        """Route after validation"""
        if state.get('error'):
            logger.info(f"[route_after_validation] Routing to error due to error: {state.get('error')}")
            return "error"
        validation_result = state.get('validation_result') or {}
        is_valid = validation_result.get('is_valid', False)

        # Debug logging
        logger.info(f"[route_after_validation] Validation result: is_valid={is_valid}")
        if not is_valid:
            error_msg = validation_result.get('error_message', 'Unknown error')
            metadata = validation_result.get('metadata') or {}
            requires_subcategory = metadata.get('requires_subcategory_selection', False)
            logger.info(f"[route_after_validation] Validation failed: {error_msg}")
            logger.info(f"[route_after_validation] Requires subcategory selection: {requires_subcategory}")
            if requires_subcategory:
                logger.info(f"[route_after_validation] Routing to generate_question for subcategory selection")
            else:
                logger.info(f"[route_after_validation] Routing to generate_question for re-asking")
        else:
            logger.info(f"[route_after_validation] Routing to update_dialog_state (valid)")

        if is_valid:
            return "valid"
        return "invalid"

    graph.add_conditional_edges(
        "validate_entity",
        route_after_validation,
        {
            "error": "handle_error",
            "valid": "update_dialog_state",
            "invalid": "generate_question"  # Re-ask with error message
        }
    )

    # update_dialog_state → check error → determine_needed_entities
    graph.add_conditional_edges(
        "update_dialog_state",
        should_route_to_error,
        {
            "error": "handle_error",
            "continue": "determine_needed_entities"
        }
    )

    # determine_needed_entities → route to generate_question (always)
    # Note: Both "all_collected" and "more_needed" go to generate_question
    # The generate_question node handles both cases (confirmation vs next question)
    graph.add_conditional_edges(
        "determine_needed_entities",
        should_route_to_error,
        {
            "error": "handle_error",
            "continue": "generate_question"
        }
    )

    # generate_question → END (always)
    # The graph ends after generating a question or confirmation
    # The next turn will start a new graph execution
    graph.add_edge("generate_question", END)

    # handle_error → END
    graph.add_edge("handle_error", END)

    # Compile graph
    compiled_graph = graph.compile()  # type: ignore
    return compiled_graph


# ============================================================
# GRAPH EXECUTION HELPER
# ============================================================

async def run_slot_filling_graph(
    state: SlotFillingState,
    db: AsyncSession,
    classifier: IntentClassifier,
    dialog_manager: DialogStateManager,
    question_generator: QuestionGenerator,
    entity_extractor: EntityExtractor,
    entity_validator: EntityValidator
) -> SlotFillingState:
    """
    Execute the Slot-Filling Graph

    Args:
        state: Initial state
        db: Database session
        classifier: Intent classifier
        dialog_manager: Dialog state manager
        question_generator: Question generator
        entity_extractor: Entity extractor
        entity_validator: Entity validator

    Returns:
        Final state after graph execution
    """
    graph = create_slot_filling_graph(
        db=db,
        classifier=classifier,
        dialog_manager=dialog_manager,
        question_generator=question_generator,
        entity_extractor=entity_extractor,
        entity_validator=entity_validator
    )

    # Execute graph
    final_state = await graph.ainvoke(state)

    # Add execution metadata
    final_state["graph_end_time"] = datetime.utcnow().isoformat()

    return final_state

