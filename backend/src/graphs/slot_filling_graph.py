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
        
        # Classify intent (context-aware)
        intent_result, classification_method = await classifier.classify(
            message=state['current_message'],
            conversation_history=state.get('conversation_history'),
            dialog_state=dialog_state
        )
        
        # Get confidence from first intent
        confidence = intent_result.intents[0].confidence if intent_result.intents else 0.0

        logger.info(f"[classify_intent_node] Intent: {intent_result.primary_intent}, Confidence: {confidence}, Method: {classification_method}")

        # Extract entities from intent result
        intent_entities = intent_result.intents[0].entities if intent_result.intents else {}

        # Merge with existing collected entities (preserve previous entities)
        existing_entities = state.get('collected_entities', {})
        merged_entities = {**existing_entities, **intent_entities}

        logger.info(f"[classify_intent_node] Existing entities: {existing_entities}, Intent entities: {intent_entities}, Merged: {merged_entities}")

        # Update state
        return {
            "intent_result": intent_result.model_dump(),
            "primary_intent": intent_result.primary_intent,
            "intent_confidence": confidence,
            "classification_method": classification_method,
            "collected_entities": merged_entities,
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
        logger.info(f"[extract_entity_node] Extracting entity: {state.get('expected_entity')}")
        
        # Extract entity
        extraction_result = await entity_extractor.extract_from_follow_up(
            message=state['current_message'],
            expected_entity=EntityType(state['expected_entity']),
            context={
                "collected_entities": state.get('collected_entities', {}),
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
            logger.warning(f"[extract_entity_node] Failed to extract entity")
            return {
                "error": {
                    "type": "EntityExtractionError",
                    "message": f"Could not extract {state.get('expected_entity')} from message",
                    "node": "extract_entity_node"
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
            
            await dialog_manager.add_entity(
                session_id=state['session_id'],
                entity_name=entity_type,
                entity_value=entity_value
            )
            
            # Remove from needed entities
            await dialog_manager.remove_needed_entity(
                session_id=state['session_id'],
                entity_name=entity_type
            )
            
            # Update state
            collected = state.get('collected_entities', {}).copy()
            collected[entity_type] = entity_value
            
            needed = [e for e in state.get('needed_entities', []) if e != entity_type]
            
            logger.info(f"[update_dialog_state_node] Added {entity_type}={entity_value}, Remaining: {needed}")
            
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
    state: SlotFillingState
) -> Dict[str, Any]:
    """
    Node: Determine which entities are still needed

    Args:
        state: Current conversation state

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
                # For booking, we need: service_type, date, time, location
                required_entities = ["service_type", "date", "time", "location"]
            elif action == "cancel":
                # For cancellation, we need: booking_id
                required_entities = ["booking_id"]
            elif action == "reschedule":
                # For rescheduling, we need: booking_id, date, time
                required_entities = ["booking_id", "date", "time"]
            elif action == "modify":
                # For modification, we need: booking_id + field to modify
                required_entities = ["booking_id"]

        # Filter out already collected entities
        needed = [e for e in required_entities if e not in collected]

        logger.info(f"[determine_needed_entities_node] Required: {required_entities}, Collected: {list(collected.keys())}, Needed: {needed}")

        return {
            "needed_entities": needed,
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
    question_generator: QuestionGenerator
) -> Dict[str, Any]:
    """
    Node: Generate question for next missing entity

    Args:
        state: Current conversation state
        question_generator: Question generator service

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
        return await determine_needed_entities_node(state)

    async def _generate_question(state):
        return await generate_question_node(state, question_generator)

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
    # classify_intent → check error → check_follow_up
    graph.add_conditional_edges(
        "classify_intent",
        should_route_to_error,
        {
            "error": "handle_error",
            "continue": "check_follow_up"
        }
    )

    # check_follow_up → route based on error or follow-up
    def route_after_follow_up_check(state: SlotFillingState) -> str:
        """Route after follow-up check"""
        if state.get('error'):
            return "error"
        if state.get('is_follow_up', False) and state.get('follow_up_confidence', 0) > 0.6:
            return "follow_up"
        return "new_intent"

    graph.add_conditional_edges(
        "check_follow_up",
        route_after_follow_up_check,
        {
            "error": "handle_error",
            "follow_up": "extract_entity",
            "new_intent": "determine_needed_entities"
        }
    )

    # extract_entity → check error → validate_entity
    graph.add_conditional_edges(
        "extract_entity",
        should_route_to_error,
        {
            "error": "handle_error",
            "continue": "validate_entity"
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

