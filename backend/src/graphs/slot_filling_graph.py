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
from typing import Dict, Any, Literal
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

        # Extract entity from message
        extraction_result = await entity_extractor.extract_from_follow_up(
            message=state['current_message'],
            expected_entity=EntityType(expected_entity),
            context={
                "collected_entities": collected_entities,
                "last_question": state.get('last_question_asked'),
                "user_id": state['user_id']
            }
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
    Node: Validate extracted entity value
    
    Args:
        state: Current conversation state
        entity_validator: Entity validator service
        
    Returns:
        Updated state with validation result
    """
    try:
        logger.info(f"[validate_entity_node] Validating entity...")

        extracted = state.get('extracted_entity', {})

        # Check if extraction was successful
        if not extracted or 'entity_type' not in extracted:
            logger.warning(f"[validate_entity_node] No entity extracted, skipping validation")
            return {
                "validation_result": {
                    "is_valid": False,
                    "error_message": "Could not extract entity from message"
                },
                "metadata": {
                    **state.get("metadata", {}),
                    "validation_skipped": True
                }
            }

        # Validate entity
        validation_result = await entity_validator.validate(
            entity_type=EntityType(extracted['entity_type']),
            value=extracted.get('normalized_value') or extracted['entity_value'],
            context={
                "user_id": state['user_id'],
                "collected_entities": state.get('collected_entities', {})
            }
        )
        
        logger.info(f"[validate_entity_node] Valid: {validation_result.is_valid}")
        
        return {
            "validation_result": validation_result.model_dump(),
            "metadata": {
                **state.get("metadata", {}),
                "nodes_executed": state.get("metadata", {}).get("nodes_executed", []) + ["validate_entity_node"]
            }
        }
    
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
        
        if validation_result.get('is_valid'):
            # Add entity to collected entities
            entity_type = extracted['entity_type']
            entity_value = validation_result['normalized_value']

            # Update in-memory state first
            collected = state.get('collected_entities', {}).copy()
            collected[entity_type] = entity_value

            needed = [e for e in state.get('needed_entities', []) if e != entity_type]

            # Save ALL collected entities to database (not just the new one)
            # This ensures that entities from previous turns are not lost
            from src.schemas.dialog_state import DialogStateUpdate
            await dialog_manager.update_state(
                session_id=state['session_id'],
                update_data=DialogStateUpdate(
                    collected_entities=collected,  # Save ALL entities
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
    db: AsyncSession = None
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
        intent_config = INTENT_CONFIGS.get(intent)
        if not intent_config:
            logger.warning(f"[determine_needed_entities_node] No config for intent: {intent}")
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
            elif action == "cancel":
                # For cancellation, we need: booking_id
                required_entities = ["booking_id"]
            elif action == "reschedule":
                # For rescheduling, we need: booking_id, date, time
                required_entities = ["booking_id", "date", "time"]
            elif action == "modify":
                # For modification, we need: booking_id + field to modify
                required_entities = ["booking_id"]
            elif action == "list":
                # For listing bookings, no additional entities needed
                required_entities = []

        # Filter out already collected entities
        needed = [e for e in required_entities if e not in collected]

        # Special check: If location is needed for booking, check if user has existing addresses
        logger.info(f"[determine_needed_entities_node] Checking auto-fill conditions: location_needed={'location' in needed}, intent={intent}, action={collected.get('action')}, db={db is not None}")

        if "location" in needed and intent == "booking_management" and collected.get("action") == "book" and db:
            # Check if user has any saved addresses
            from src.core.models import Address
            user_id = state.get('user_id')
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

                await dialog_manager.update_state(
                    session_id=state['session_id'],
                    update_data=DialogStateUpdate(
                        state=DialogStateType.AWAITING_CONFIRMATION,
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
            intent_enum = IntentType(primary_intent) if isinstance(primary_intent, str) else primary_intent

            original_question = question_generator.generate(
                entity_type=EntityType(next_entity),
                intent=intent_enum,
                collected_entities=state.get('collected_entities', {})
            )
            question += original_question
        else:
            # Generate new question
            primary_intent = state.get('primary_intent')
            intent_enum = IntentType(primary_intent) if isinstance(primary_intent, str) else primary_intent

            question = question_generator.generate(
                entity_type=EntityType(next_entity),
                intent=intent_enum,
                collected_entities=state.get('collected_entities', {})
            )

        logger.info(f"[generate_question_node] Question: {question[:100]}...")

        # Save last_question_asked to dialog state context for follow-up detection
        try:
            from src.schemas.dialog_state import DialogStateUpdate
            await dialog_manager.update_state(
                session_id=state['session_id'],
                update_data=DialogStateUpdate(
                    context={"last_question": question, "expected_entity": next_entity}
                )
            )
            logger.info(f"[generate_question_node] ✅ Saved last_question to dialog state context")
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

        error = state.get('error', {})
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
    if state.get('is_follow_up', False) and state.get('follow_up_confidence', 0) > 0.6:
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
    validation_result = state.get('validation_result', {})
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
) -> StateGraph:
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
        if state.get('is_follow_up', False) and state.get('follow_up_confidence', 0) > 0.6:
            logger.info("[route_after_follow_up_check] Routing to: follow_up")
            return "follow_up"
        # Check if intent has changed (user is asking a different question)
        if state.get('intent_changed', False):
            logger.info("[route_after_follow_up_check] Routing to: intent_changed (EXIT)")
            return "intent_changed"
        logger.info("[route_after_follow_up_check] Routing to: new_intent")
        return "new_intent"

    graph.add_conditional_edges(
        "check_follow_up",
        route_after_follow_up_check,
        {
            "error": "handle_error",
            "follow_up": "extract_entity",
            "intent_changed": END,  # Exit slot-filling, let coordinator handle new intent
            "new_intent": "determine_needed_entities"
        }
    )

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
            return "error"
        validation_result = state.get('validation_result', {})
        if validation_result.get('is_valid', False):
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
    return graph.compile()


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

