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
        
        Args:
            user: Current user
            request: Chat message request
            
        Returns:
            ChatMessageResponse with user and AI messages
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
        
        # 3. TODO: Call agentic flow (intent classification + agent routing)
        # For now, return a placeholder response
        ai_response_text = await self._get_ai_response(request.message, session_id, user)
        
        # Calculate response time
        response_time_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
        
        # 4. Store AI response
        ai_message = await self._store_message(
            user_id=user.id,
            session_id=session_id,
            role=MessageRole.ASSISTANT,
            message=ai_response_text,
            channel=Channel(request.channel),
            response_time_ms=response_time_ms
        )
        
        # 5. Return response
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
        user: User
    ) -> str:
        """
        Get AI response for user message
        
        TODO: Replace with full agentic flow:
        ================================================
        1. Intent Classification
           - Classify user intent (book_service, price_inquiry, etc.)
           - Extract entities from message
           - Calculate confidence score
        
        2. Agent Routing
           - Route to appropriate agent based on intent:
             * BookingAgent - for booking/rescheduling/cancellation
             * SQLAgent - for pricing/availability queries
             * RAGAgent - for service information
             * PolicyAgent - for policy/terms queries
             * ComplaintAgent - for complaints/issues
             * PaymentAgent - for payment queries
             * RefundAgent - for refund requests
        
        3. RAG Pipeline
           - Retrieve relevant documents from vector store
           - Provide context to agents
        
        4. Multi-Agent Orchestration (LangGraph)
           - Coordinate multiple agents if needed
           - Handle complex multi-step workflows
        
        5. Response Generation
           - Generate natural language response
           - Include provenance (sources used)
           - Calculate quality metrics (grounding, faithfulness, relevancy)
        
        6. Store Metadata
           - Store intent, confidence, agent_calls, provenance
           - Flag for review if needed
        ================================================
        
        For now: Return helpful placeholder response
        """
        logger.info(f"Processing message for user {user.id} in session {session_id}")
        
        # TODO: Implement full ChatService with agentic flow
        # This is a placeholder until we implement:
        # - Intent classification system
        # - Agent routing logic
        # - RAG retrieval pipeline
        # - LangGraph orchestration
        
        return (
            f"Hello {user.name}! I'm ConvergeAI assistant. "
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

