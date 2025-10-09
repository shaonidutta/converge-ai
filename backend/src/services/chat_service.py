"""
Chat Service
Business logic for chat operations
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from datetime import datetime, timezone
from typing import Optional, List
import uuid
import logging

from src.core.models import Conversation, User
from src.core.models.conversation import MessageRole, Channel
from src.schemas.chat import (
    ChatMessageRequest,
    ChatMessageResponse,
    ChatHistoryResponse,
    MessageResponse,
    SessionResponse,
)

logger = logging.getLogger(__name__)


class ChatService:
    """Service class for chat business logic"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def send_message(
        self,
        user: User,
        request: ChatMessageRequest
    ) -> ChatMessageResponse:
        """
        Send a chat message and get AI response

        Now powered by intelligent slot-filling system!

        The system will:
        1. Classify your intent (booking, pricing, policy, etc.)
        2. Extract entities from your message
        3. Ask follow-up questions to collect missing information
        4. Validate all inputs
        5. Generate confirmation before executing actions

        Args:
            user: Current user
            request: Chat message request

        Returns:
            ChatMessageResponse with user and AI messages, including metadata
        """
        start_time = datetime.now(timezone.utc)

        # 1. Get or create session
        session_id = request.session_id or self._generate_session_id()

        # 2. Store user message
        user_message = await self._store_message(
            user_id=user.id,
            session_id=session_id,
            role=MessageRole.USER,
            message=request.message,
            channel=Channel(request.channel)
        )

        # 3. Get AI response with metadata from slot-filling system
        ai_response_text, metadata = await self._get_ai_response(
            user_message=request.message,
            session_id=session_id,
            user=user,
            channel=request.channel
        )

        # Calculate response time
        response_time_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)

        # 4. Store AI response with metadata
        ai_message = await self._store_message(
            user_id=user.id,
            session_id=session_id,
            role=MessageRole.ASSISTANT,
            message=ai_response_text,
            channel=Channel(request.channel),
            intent=metadata.get("intent"),
            intent_confidence=metadata.get("intent_confidence"),
            response_time_ms=response_time_ms,
            agent_calls=metadata  # Store full metadata in JSON field
        )

        # 5. Return response
        logger.info(f"[ChatService] Message processed successfully: session={session_id}, response_time={response_time_ms}ms")
        return ChatMessageResponse(
            session_id=session_id,
            user_message=self._to_message_response(user_message),
            assistant_message=self._to_message_response(ai_message),
            response_time_ms=response_time_ms
        )
    
    async def _get_ai_response(
        self,
        user_message: str,
        session_id: str,
        user: User,
        channel: str = "web"
    ) -> tuple[str, dict]:
        """
        Get AI response using slot-filling workflow

        This method now uses the intelligent slot-filling system to:
        1. Classify user intent (context-aware)
        2. Extract entities from message
        3. Ask follow-up questions for missing information
        4. Validate all inputs
        5. Generate confirmation before executing actions

        Args:
            user_message: User's message
            session_id: Session ID
            user: User object
            channel: Communication channel (web, mobile, whatsapp)

        Returns:
            Tuple of (response_text, metadata_dict)

        Metadata includes:
            - intent: Detected intent
            - intent_confidence: Confidence score
            - response_type: Type of response (question, confirmation, error, ready_for_agent)
            - collected_entities: Entities collected so far
            - needed_entities: Entities still needed
            - should_trigger_agent: Whether to trigger agent execution
            - classification_method: How intent was classified (pattern/llm/fallback)
            - nodes_executed: List of graph nodes executed
            - error: Error message if any
        """
        logger.info(f"[ChatService] Processing message for user {user.id} in session {session_id}")
        logger.debug(f"[ChatService] Message: {user_message[:100]}...")

        try:
            # Import service factory
            from src.services.service_factory import SlotFillingServiceFactory
            from src.core.config import settings

            # Check if slot-filling is enabled
            if not settings.ENABLE_SLOT_FILLING:
                logger.warning("[ChatService] Slot-filling is disabled, using fallback response")
                return self._get_fallback_response(user, user_message), {}

            # 1. Initialize slot-filling service with all dependencies
            logger.debug("[ChatService] Initializing slot-filling service...")
            slot_filling_service = await SlotFillingServiceFactory.create(self.db)

            # 2. Process message through slot-filling graph
            logger.debug("[ChatService] Running slot-filling graph...")
            result = await slot_filling_service.process_message(
                message=user_message,
                session_id=session_id,
                user=user,
                channel=channel
            )

            # 3. Extract metadata
            metadata = {
                "intent": result.metadata.get("primary_intent"),
                "intent_confidence": result.metadata.get("intent_confidence"),
                "response_type": result.response_type,
                "collected_entities": result.collected_entities,
                "needed_entities": result.needed_entities,
                "should_trigger_agent": result.should_trigger_agent,
                "classification_method": result.metadata.get("classification_method"),
                "nodes_executed": result.metadata.get("nodes_executed", []),
                "slot_filling_metadata": result.metadata  # Store full metadata
            }

            logger.info(f"[ChatService] Intent: {metadata['intent']}")
            logger.info(f"[ChatService] Confidence: {metadata['intent_confidence']}")
            logger.info(f"[ChatService] Response type: {metadata['response_type']}")
            logger.info(f"[ChatService] Should trigger agent: {metadata['should_trigger_agent']}")

            # 4. TODO: If should_trigger_agent=True, trigger agent execution
            # For now, just return the confirmation and mark as ready_for_agent
            if result.should_trigger_agent:
                logger.info("[ChatService] Agent execution required (deferred to background worker)")
                # TODO: Enqueue agent execution task
                # await agent_execution_queue.enqueue(session_id, user.id, result.collected_entities)

            return result.final_response, metadata

        except Exception as e:
            logger.error(f"[ChatService] Slot-filling error: {e}", exc_info=True)

            # Return fallback response with error metadata
            fallback_response = (
                "I apologize, but I'm having trouble processing your request right now. "
                "Please try again or contact support if the issue persists."
            )

            error_metadata = {
                "error": str(e),
                "error_type": type(e).__name__,
                "fallback_used": True,
                "original_message": user_message
            }

            return fallback_response, error_metadata

    def _get_fallback_response(self, user: User, user_message: str) -> str:
        """
        Get fallback response when slot-filling is disabled or fails

        Args:
            user: User object
            user_message: User's message

        Returns:
            Fallback response text
        """
        user_name = f"{user.first_name} {user.last_name}".strip() if user.first_name or user.last_name else "there"

        return (
            f"Hello {user_name}! I'm ConvergeAI assistant. "
            "I can help you with:\n\n"
            "🔹 Booking home services (AC, plumbing, cleaning, etc.)\n"
            "🔹 Checking prices and availability\n"
            "🔹 Service information and recommendations\n"
            "🔹 Managing your bookings\n"
            "🔹 Handling complaints and issues\n"
            "🔹 Payment and refund queries\n\n"
            f"You said: '{user_message}'\n\n"
            "Our AI agents are being configured to provide you with intelligent assistance. "
            "Soon, I'll be able to understand your intent and route you to the right specialist!"
        )
    
    async def _store_message(
        self,
        user_id: int,
        session_id: str,
        role: MessageRole,
        message: str,
        channel: Channel,
        intent: Optional[str] = None,
        intent_confidence: Optional[float] = None,
        response_time_ms: Optional[int] = None,
        agent_calls: Optional[dict] = None,
        provenance: Optional[dict] = None,
        grounding_score: Optional[float] = None,
        faithfulness_score: Optional[float] = None,
        relevancy_score: Optional[float] = None
    ) -> Conversation:
        """
        Store a message in the conversations table
        
        Args:
            user_id: User ID
            session_id: Session ID
            role: Message role (USER or ASSISTANT)
            message: Message text
            channel: Communication channel
            intent: Detected intent (optional)
            intent_confidence: Intent confidence score (optional)
            response_time_ms: Response time in milliseconds (optional)
            agent_calls: Agent execution details (optional)
            provenance: Source tracking (optional)
            grounding_score: Grounding quality score (optional)
            faithfulness_score: Faithfulness quality score (optional)
            relevancy_score: Relevancy quality score (optional)
            
        Returns:
            Stored Conversation object
        """
        conversation = Conversation(
            user_id=user_id,
            session_id=session_id,
            role=role,
            message=message,
            channel=channel,
            intent=intent,
            intent_confidence=intent_confidence,
            response_time_ms=response_time_ms,
            agent_calls=agent_calls,
            provenance=provenance,
            grounding_score=grounding_score,
            faithfulness_score=faithfulness_score,
            relevancy_score=relevancy_score
        )
        
        self.db.add(conversation)
        await self.db.commit()
        await self.db.refresh(conversation)
        
        logger.info(f"Stored message: session={session_id}, role={role.value}, id={conversation.id}")
        return conversation
    
    async def get_history(
        self,
        user: User,
        session_id: str,
        limit: int = 50,
        skip: int = 0
    ) -> ChatHistoryResponse:
        """
        Get chat history for a session
        
        Args:
            user: Current user
            session_id: Session ID
            limit: Maximum number of messages to retrieve
            skip: Number of messages to skip
            
        Returns:
            ChatHistoryResponse with messages
        """
        # Get messages
        query = (
            select(Conversation)
            .where(
                Conversation.user_id == user.id,
                Conversation.session_id == session_id
            )
            .order_by(Conversation.created_at.asc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        messages = result.scalars().all()
        
        # Get total count
        count_query = select(func.count(Conversation.id)).where(
            Conversation.user_id == user.id,
            Conversation.session_id == session_id
        )
        total = await self.db.scalar(count_query)
        
        logger.info(f"Retrieved {len(messages)} messages for session {session_id}")
        
        return ChatHistoryResponse(
            session_id=session_id,
            messages=[self._to_message_response(msg) for msg in messages],
            total=total or 0
        )
    
    async def list_sessions(self, user: User) -> List[SessionResponse]:
        """
        List all chat sessions for a user

        Args:
            user: Current user

        Returns:
            List of SessionResponse objects
        """
        query = (
            select(
                Conversation.session_id,
                func.count(Conversation.id).label('message_count'),
                func.max(Conversation.created_at).label('last_message_at'),
                func.min(Conversation.created_at).label('first_message_at')
            )
            .where(Conversation.user_id == user.id)
            .group_by(Conversation.session_id)
            .order_by(desc('last_message_at'))
        )

        result = await self.db.execute(query)
        sessions = result.all()

        logger.info(f"Retrieved {len(sessions)} sessions for user {user.id}")

        return [
            SessionResponse(
                session_id=session.session_id,
                message_count=session.message_count,
                last_message_at=session.last_message_at,
                first_message_at=session.first_message_at
            )
            for session in sessions
        ]

    async def delete_session(self, user: User, session_id: str) -> None:
        """
        Delete a chat session and all its messages

        Args:
            user: Current user
            session_id: Session ID to delete

        Raises:
            ValueError: If session not found or doesn't belong to user
        """
        from sqlalchemy import delete as sql_delete

        # Check if session exists and belongs to user
        check_query = select(func.count(Conversation.id)).where(
            Conversation.user_id == user.id,
            Conversation.session_id == session_id
        )
        count = await self.db.scalar(check_query)

        if not count or count == 0:
            raise ValueError(f"Session {session_id} not found or doesn't belong to user")

        # Delete all messages in the session
        delete_query = sql_delete(Conversation).where(
            Conversation.user_id == user.id,
            Conversation.session_id == session_id
        )
        await self.db.execute(delete_query)
        await self.db.commit()

        logger.info(f"Deleted session {session_id} for user {user.id} ({count} messages)")

    
    def _generate_session_id(self) -> str:
        """Generate a unique session ID"""
        return f"session_{uuid.uuid4().hex[:16]}"
    
    def _to_message_response(self, conversation: Conversation) -> MessageResponse:
        """Convert Conversation model to MessageResponse"""
        return MessageResponse(
            id=conversation.id,
            role=conversation.role.value,
            message=conversation.message,
            intent=conversation.intent,
            intent_confidence=float(conversation.intent_confidence) if conversation.intent_confidence else None,
            created_at=conversation.created_at
        )

