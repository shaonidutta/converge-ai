"""
Slot-Filling Orchestrator Service

High-level orchestrator that manages the slot-filling workflow using LangGraph.

Responsibilities:
- Initialize all required services
- Create initial conversation state
- Run the slot-filling graph
- Return final response with metadata

Design Principles:
- Thin orchestrator (delegates to graph and services)
- Clear separation of concerns
- Comprehensive error handling
- Rich metadata for debugging
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.nlp.intent.classifier import IntentClassifier
from src.services.dialog_state_manager import DialogStateManager
from src.services.question_generator import QuestionGenerator
from src.services.entity_extractor import EntityExtractor
from src.services.entity_validator import EntityValidator
from src.graphs.state import create_initial_state
# Import run_slot_filling_graph inside function to avoid circular import
from src.core.models import User

logger = logging.getLogger(__name__)


class SlotFillingResponse(BaseModel):
    """Response from slot-filling workflow"""
    final_response: str
    response_type: str  # "question", "confirmation", "error", "ready_for_agent"
    collected_entities: Dict[str, Any]
    needed_entities: List[str]
    should_trigger_agent: bool
    metadata: Dict[str, Any]


class SlotFillingService:
    """
    Slot-Filling Orchestrator Service
    
    Manages the complete slot-filling workflow:
    1. Intent classification (context-aware)
    2. Follow-up detection
    3. Entity extraction
    4. Entity validation
    5. Question generation
    6. Confirmation
    7. Agent triggering
    """
    
    def __init__(
        self,
        db: AsyncSession,
        classifier: IntentClassifier,
        dialog_manager: DialogStateManager,
        question_generator: QuestionGenerator,
        entity_extractor: EntityExtractor,
        entity_validator: EntityValidator
    ):
        self.db = db
        self.classifier = classifier
        self.dialog_manager = dialog_manager
        self.question_generator = question_generator
        self.entity_extractor = entity_extractor
        self.entity_validator = entity_validator
    
    async def process_message(
        self,
        message: str,
        session_id: str,
        user: User,
        channel: str = "web"
    ) -> SlotFillingResponse:
        """
        Process user message through slot-filling workflow
        
        Args:
            message: User's message
            session_id: Session ID
            user: User object
            channel: Communication channel (web, mobile, etc.)
            
        Returns:
            SlotFillingResponse with final_response, response_type, metadata
        """
        logger.info(f"[SlotFillingService] Processing message for user {user.id}, session {session_id}")
        logger.info(f"[SlotFillingService] Message: {message}")

        try:
            # Import here to avoid circular import
            from src.graphs.slot_filling_graph import run_slot_filling_graph

            # 1. Get conversation history
            history = await self._get_conversation_history(session_id, limit=10)

            # 2. Load existing dialog state to get previously collected entities
            dialog_state = await self.dialog_manager.get_active_state(session_id)
            collected_entities = dialog_state.collected_entities if dialog_state else {}
            needed_entities = dialog_state.needed_entities if dialog_state else []
            last_question = dialog_state.context.get('last_question') if dialog_state and dialog_state.context else None

            # Import DialogStateType for comparison
            from src.core.models.dialog_state import DialogStateType
            is_awaiting_confirmation = (
                dialog_state and
                dialog_state.state == DialogStateType.AWAITING_CONFIRMATION
            )

            logger.info(f"[SlotFillingService] Loaded dialog state: state={dialog_state.state.value if dialog_state else None}, collected={collected_entities}, needed={needed_entities}, last_question={last_question is not None}, awaiting_confirmation={is_awaiting_confirmation}")

            # 3. Check if user is confirming (responding to confirmation prompt)
            if is_awaiting_confirmation:
                message_lower = message.lower().strip()
                confirmation_keywords = ["yes", "yeah", "yep", "sure", "ok", "okay", "correct", "right", "confirm", "proceed"]
                rejection_keywords = ["no", "nope", "cancel", "stop", "don't", "dont"]

                if any(keyword == message_lower for keyword in confirmation_keywords):
                    logger.info(f"[SlotFillingService] User confirmed, triggering agent execution")
                    # User confirmed, return response that triggers agent
                    return SlotFillingResponse(
                        final_response="Confirmed",
                        response_type="ready_for_agent",
                        collected_entities=collected_entities,
                        needed_entities=[],
                        should_trigger_agent=True,
                        metadata={
                            "intent": dialog_state.intent,
                            "intent_confidence": 0.95,
                            "dialog_state_type": "awaiting_confirmation",
                            "user_confirmed": True
                        }
                    )
                elif any(keyword in message_lower for keyword in rejection_keywords):
                    logger.info(f"[SlotFillingService] User rejected confirmation, clearing dialog state")
                    # User rejected, clear dialog state
                    await self.dialog_manager.clear_state(session_id)
                    return SlotFillingResponse(
                        final_response="Okay, I've cancelled that request. How else can I help you?",
                        response_type="acknowledgment",
                        collected_entities={},
                        needed_entities=[],
                        should_trigger_agent=False,
                        metadata={
                            "user_confirmed": False,
                            "dialog_cleared": True
                        }
                    )

            # 4. Create initial state with previously collected entities
            state = create_initial_state(
                user_id=user.id,
                session_id=session_id,
                current_message=message,
                channel=channel,
                conversation_history=history
            )

            # Populate with previously collected entities and last question
            state['collected_entities'] = collected_entities
            state['needed_entities'] = needed_entities
            if last_question:
                state['last_question_asked'] = last_question

            # Load metadata from dialog state context (includes available_subcategories, service_type, needed_entities, etc.)
            if dialog_state and dialog_state.context:
                try:
                    # Context is a JSON field, should be a dict
                    context_data = dialog_state.context if isinstance(dialog_state.context, dict) else {}

                    # Extract metadata-like fields from context
                    if 'available_subcategories' in context_data:
                        state['metadata'] = {**state.get('metadata', {}), 'available_subcategories': context_data['available_subcategories']}
                        logger.info(f"[SlotFillingService] Loaded {len(context_data['available_subcategories'])} available_subcategories from dialog state context")

                    # Also load service_type if present
                    if 'service_type' in context_data:
                        state['metadata'] = {**state.get('metadata', {}), 'service_type': context_data['service_type']}
                        logger.info(f"[SlotFillingService] Loaded service_type from dialog state context: {context_data['service_type']}")

                    # Load needed_entities from context (overrides the one from dialog_state.needed_entities)
                    # This is important because needed_entities can be updated during validation
                    if 'needed_entities' in context_data:
                        state['needed_entities'] = context_data['needed_entities']
                        logger.info(f"[SlotFillingService] Loaded needed_entities from dialog state context: {context_data['needed_entities']}")

                except Exception as e:
                    logger.warning(f"[SlotFillingService] Could not load dialog state context: {e}")
                    # Continue without metadata

            # 4. Run slot-filling graph
            logger.info("[SlotFillingService] Running slot-filling graph...")
            final_state = await run_slot_filling_graph(
                state=state,
                db=self.db,
                classifier=self.classifier,
                dialog_manager=self.dialog_manager,
                question_generator=self.question_generator,
                entity_extractor=self.entity_extractor,
                entity_validator=self.entity_validator
            )
            
            # 4. Build response
            response = self._build_response(final_state)

            logger.info(f"[SlotFillingService] Response type: {response.response_type}")
            logger.info(f"[SlotFillingService] Should trigger agent: {response.should_trigger_agent}")
            
            return response
        
        except Exception as e:
            logger.error(f"[SlotFillingService] Error processing message: {e}", exc_info=True)
            
            # Return error response
            return SlotFillingResponse(
                final_response="Sorry, I encountered an error processing your request. Please try again.",
                response_type="error",
                collected_entities={},
                needed_entities=[],
                should_trigger_agent=False,
                metadata={
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
            )
    
    async def _get_conversation_history(
        self,
        session_id: str,
        limit: int = 10
    ) -> List[Dict[str, str]]:
        """
        Get conversation history for session from Conversation table

        Args:
            session_id: Session ID
            limit: Maximum number of messages to retrieve

        Returns:
            List of conversation messages in chronological order
        """
        try:
            from src.core.models import Conversation
            from sqlalchemy import select, asc

            # Get messages in chronological order (oldest first)
            result = await self.db.execute(
                select(Conversation)
                .where(Conversation.session_id == session_id)
                .order_by(asc(Conversation.created_at))
                .limit(limit)
            )
            messages = result.scalars().all()

            # Convert to expected format
            history = []
            for msg in messages:
                history.append({
                    "role": msg.role.value,  # Convert enum to string: "user" or "assistant"
                    "content": msg.message,  # Use "content" key (not "message")
                    "timestamp": msg.created_at.isoformat()
                })

            logger.debug(f"[SlotFillingService] Retrieved {len(history)} messages for session {session_id}")
            return history

        except Exception as e:
            logger.error(f"[SlotFillingService] Error getting conversation history: {e}", exc_info=True)
            return []
    
    def _build_response(self, final_state: Dict[str, Any]) -> SlotFillingResponse:
        """
        Build SlotFillingResponse from final graph state
        
        Args:
            final_state: Final state from slot-filling graph
            
        Returns:
            SlotFillingResponse
        """
        # Determine response type
        response_type = self._determine_response_type(final_state)

        # Check if should trigger agent
        # IMPORTANT: Do NOT trigger agent if we're awaiting confirmation
        dialog_state_type = final_state.get("dialog_state_type", "")
        is_awaiting_confirmation = (
            dialog_state_type == "awaiting_confirmation" or
            response_type == "confirmation"
        )

        should_trigger_agent = (
            final_state.get("next_graph") == "agent_execution" or
            (len(final_state.get("needed_entities", [])) == 0 and
             final_state.get("primary_intent") is not None and
             not is_awaiting_confirmation)  # Don't trigger if awaiting confirmation
        )
        
        return SlotFillingResponse(
            final_response=final_state.get("final_response", ""),
            response_type=response_type,
            collected_entities=final_state.get("collected_entities", {}),
            needed_entities=final_state.get("needed_entities", []),
            should_trigger_agent=should_trigger_agent,
            metadata={
                "intent": final_state.get("primary_intent"),
                "intent_confidence": final_state.get("intent_confidence"),
                "is_follow_up": final_state.get("is_follow_up"),
                "dialog_state_type": final_state.get("dialog_state_type"),
                "retry_count": final_state.get("retry_count", 0),
                "timestamp": datetime.now().isoformat(),
                "provenance": final_state.get("provenance"),
                "intent_changed": final_state.get("intent_changed", False),
                "original_intent": final_state.get("original_intent")
            }
        )
    
    def _determine_response_type(self, final_state: Dict[str, Any]) -> str:
        """
        Determine response type from final state
        
        Returns:
            "question", "confirmation", "error", "ready_for_agent", "acknowledgment"
        """
        if final_state.get("error"):
            return "error"
        
        if final_state.get("current_question"):
            return "question"
        
        if final_state.get("confirmation_message"):
            return "confirmation"
        
        if final_state.get("next_graph") == "agent_execution":
            return "ready_for_agent"
        
        if len(final_state.get("needed_entities", [])) == 0:
            return "ready_for_agent"
        
        return "acknowledgment"
    
    async def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """
        Get current status of a session
        
        Args:
            session_id: Session ID
            
        Returns:
            Dict with session status information
        """
        try:
            dialog_state = await self.dialog_manager.get_active_state(session_id)
            
            if not dialog_state:
                return {
                    "session_id": session_id,
                    "status": "idle",
                    "collected_entities": {},
                    "needed_entities": []
                }
            
            return {
                "session_id": session_id,
                "status": dialog_state.state.value,
                "intent": dialog_state.intent,
                "collected_entities": dialog_state.collected_entities,
                "needed_entities": dialog_state.needed_entities,
                "has_pending_action": dialog_state.has_pending_action(),
                "is_expired": dialog_state.is_expired()
            }
        
        except Exception as e:
            logger.error(f"[SlotFillingService] Error getting session status: {e}")
            return {
                "session_id": session_id,
                "status": "error",
                "error": str(e)
            }
    
    async def clear_session(self, session_id: str) -> bool:
        """
        Clear session state (reset conversation)
        
        Args:
            session_id: Session ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            await self.dialog_manager.clear_state(session_id)
            logger.info(f"[SlotFillingService] Cleared session: {session_id}")
            return True
        except Exception as e:
            logger.error(f"[SlotFillingService] Error clearing session: {e}")
            return False

