"""
Dialog State Manager Service

Manages conversation state for multi-turn dialogs.
Enables context tracking, slot-filling, and follow-up response handling.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, List, Any
import logging
import re

from src.core.models import DialogState, User
from src.core.models.dialog_state import DialogStateType
from src.schemas.dialog_state import (
    DialogStateCreate,
    DialogStateUpdate,
    DialogStateResponse,
    DialogStateStatus,
    FollowUpDetectionResult
)

logger = logging.getLogger(__name__)


class DialogStateManager:
    """
    Service class for dialog state management
    
    Responsibilities:
    - Create and retrieve dialog states
    - Update state as conversation progresses
    - Detect follow-up responses
    - Clean up expired states
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_active_state(
        self,
        session_id: str
    ) -> Optional[DialogState]:
        """
        Get active dialog state for a session
        
        Args:
            session_id: Session identifier
            
        Returns:
            DialogState if active state exists, None otherwise
        """
        query = select(DialogState).where(
            DialogState.session_id == session_id
        )
        result = await self.db.execute(query)
        state = result.scalar_one_or_none()
        
        if state and state.is_expired():
            logger.info(f"Dialog state expired for session {session_id}, cleaning up")
            await self.clear_state(session_id)
            return None
        
        return state
    
    async def create_state(
        self,
        create_data: DialogStateCreate
    ) -> DialogState:
        """
        Create a new dialog state
        
        Args:
            create_data: Dialog state creation data
            
        Returns:
            Created DialogState object
        """
        # Check if state already exists for this session
        existing_state = await self.get_active_state(create_data.session_id)
        if existing_state:
            logger.warning(f"Dialog state already exists for session {create_data.session_id}, updating instead")
            return await self.update_state(
                create_data.session_id,
                DialogStateUpdate(
                    state=create_data.state,
                    intent=create_data.intent,
                    collected_entities=create_data.collected_entities,
                    needed_entities=create_data.needed_entities,
                    pending_action=create_data.pending_action,
                    context=create_data.context
                )
            )
        
        # Calculate expiration time
        expires_at = datetime.now(timezone.utc) + timedelta(hours=create_data.expires_in_hours)
        
        # Create new state
        dialog_state = DialogState(
            user_id=create_data.user_id,
            session_id=create_data.session_id,
            state=create_data.state,
            intent=create_data.intent,
            collected_entities=create_data.collected_entities or {},
            needed_entities=create_data.needed_entities or [],
            pending_action=create_data.pending_action,
            context=create_data.context or {},
            expires_at=expires_at
        )
        
        self.db.add(dialog_state)
        await self.db.commit()
        await self.db.refresh(dialog_state)
        
        logger.info(f"Created dialog state for session {create_data.session_id}: state={create_data.state}, intent={create_data.intent}")
        return dialog_state
    
    async def update_state(
        self,
        session_id: str,
        update_data: DialogStateUpdate
    ) -> DialogState:
        """
        Update an existing dialog state
        
        Args:
            session_id: Session identifier
            update_data: Update data
            
        Returns:
            Updated DialogState object
            
        Raises:
            ValueError: If state doesn't exist
        """
        state = await self.get_active_state(session_id)
        if not state:
            raise ValueError(f"No active dialog state found for session {session_id}")
        
        # Update fields if provided
        if update_data.state is not None:
            state.state = update_data.state
        
        if update_data.intent is not None:
            state.intent = update_data.intent
        
        if update_data.collected_entities is not None:
            # Merge with existing entities
            state.collected_entities = {
                **state.collected_entities,
                **update_data.collected_entities
            }
        
        if update_data.needed_entities is not None:
            # Replace needed entities
            state.needed_entities = update_data.needed_entities
        
        if update_data.pending_action is not None:
            state.pending_action = update_data.pending_action
        
        if update_data.context is not None:
            # Merge with existing context
            state.context = {
                **state.context,
                **update_data.context
            }
        
        if update_data.expires_in_hours is not None:
            state.expires_at = datetime.now(timezone.utc) + timedelta(hours=update_data.expires_in_hours)
        
        await self.db.commit()
        await self.db.refresh(state)
        
        logger.info(f"Updated dialog state for session {session_id}: state={state.state}, intent={state.intent}")
        return state
    
    async def clear_state(self, session_id: str) -> bool:
        """
        Clear dialog state for a session
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if state was cleared, False if no state existed
        """
        query = delete(DialogState).where(
            DialogState.session_id == session_id
        )
        result = await self.db.execute(query)
        await self.db.commit()
        
        cleared = result.rowcount > 0
        if cleared:
            logger.info(f"Cleared dialog state for session {session_id}")
        
        return cleared
    
    async def add_entity(
        self,
        session_id: str,
        entity_name: str,
        entity_value: Any
    ) -> DialogState:
        """
        Add a single entity to collected_entities
        
        Args:
            session_id: Session identifier
            entity_name: Name of the entity
            entity_value: Value of the entity
            
        Returns:
            Updated DialogState object
        """
        return await self.update_state(
            session_id,
            DialogStateUpdate(
                collected_entities={entity_name: entity_value}
            )
        )
    
    async def remove_needed_entity(
        self,
        session_id: str,
        entity_name: str
    ) -> DialogState:
        """
        Remove an entity from needed_entities list
        
        Args:
            session_id: Session identifier
            entity_name: Name of the entity to remove
            
        Returns:
            Updated DialogState object
        """
        state = await self.get_active_state(session_id)
        if not state:
            raise ValueError(f"No active dialog state found for session {session_id}")
        
        if entity_name in state.needed_entities:
            needed = [e for e in state.needed_entities if e != entity_name]
            return await self.update_state(
                session_id,
                DialogStateUpdate(needed_entities=needed)
            )
        
        return state
    
    async def get_state_status(
        self,
        session_id: str
    ) -> DialogStateStatus:
        """
        Get dialog state status for a session
        
        Args:
            session_id: Session identifier
            
        Returns:
            DialogStateStatus with active state info
        """
        state = await self.get_active_state(session_id)
        
        has_active = state is not None and state.is_active()
        is_follow_up_likely = has_active and (
            state.state == DialogStateType.COLLECTING_INFO or
            state.state == DialogStateType.AWAITING_CONFIRMATION
        )
        
        return DialogStateStatus(
            has_active_state=has_active,
            state=DialogStateResponse.model_validate(state) if state else None,
            is_follow_up_likely=is_follow_up_likely
        )

    async def is_follow_up_response(
        self,
        message: str,
        session_id: str
    ) -> FollowUpDetectionResult:
        """
        Detect if a message is a follow-up response to a previous question

        Uses heuristics:
        1. Active dialog state exists
        2. Message is short (< 10 words)
        3. Message matches expected patterns (yes/no, single entity value)
        4. Dialog state is collecting info or awaiting confirmation

        Args:
            message: User message
            session_id: Session identifier

        Returns:
            FollowUpDetectionResult with detection details
        """
        state = await self.get_active_state(session_id)

        # No active state = not a follow-up
        if not state or not state.is_active():
            return FollowUpDetectionResult(
                is_follow_up=False,
                confidence=1.0,
                reason="No active dialog state exists",
                expected_entity=None
            )

        # State is idle or completed = not a follow-up
        if state.state in [DialogStateType.IDLE, DialogStateType.COMPLETED]:
            return FollowUpDetectionResult(
                is_follow_up=False,
                confidence=0.9,
                reason=f"Dialog state is {state.state.value}, not expecting follow-up",
                expected_entity=None
            )

        # Analyze message characteristics
        message_lower = message.lower().strip()
        word_count = len(message_lower.split())

        # Check for confirmation keywords (yes/no)
        confirmation_keywords = {
            'yes': ['yes', 'yeah', 'yep', 'sure', 'ok', 'okay', 'correct', 'right', 'confirm'],
            'no': ['no', 'nope', 'nah', 'not', 'cancel', 'wrong']
        }

        is_confirmation = any(
            keyword in message_lower
            for keywords in confirmation_keywords.values()
            for keyword in keywords
        )

        # If awaiting confirmation and message is confirmation keyword
        if state.state == DialogStateType.AWAITING_CONFIRMATION and is_confirmation:
            return FollowUpDetectionResult(
                is_follow_up=True,
                confidence=0.95,
                reason="Dialog state is awaiting confirmation and message contains confirmation keyword",
                expected_entity="confirmation"
            )

        # If collecting info and message is short
        if state.state == DialogStateType.COLLECTING_INFO:
            if word_count <= 10:
                # Check if message might be an entity value
                expected_entity = state.needed_entities[0] if state.needed_entities else None

                # Very short messages (1-3 words) are likely entity values
                if word_count <= 3:
                    return FollowUpDetectionResult(
                        is_follow_up=True,
                        confidence=0.9,
                        reason=f"Dialog state is collecting info, message is very short ({word_count} words), likely entity value",
                        expected_entity=expected_entity
                    )

                # Medium short messages (4-10 words) are probably entity values
                return FollowUpDetectionResult(
                    is_follow_up=True,
                    confidence=0.75,
                    reason=f"Dialog state is collecting info, message is short ({word_count} words), possibly entity value",
                    expected_entity=expected_entity
                )

        # Message is long, probably a new intent
        if word_count > 10:
            return FollowUpDetectionResult(
                is_follow_up=False,
                confidence=0.7,
                reason=f"Message is long ({word_count} words), likely a new intent despite active dialog state",
                expected_entity=None
            )

        # Default: active state exists but unclear
        return FollowUpDetectionResult(
            is_follow_up=True,
            confidence=0.6,
            reason="Active dialog state exists, treating as potential follow-up",
            expected_entity=state.needed_entities[0] if state.needed_entities else None
        )

    async def cleanup_expired_states(self) -> int:
        """
        Clean up expired dialog states

        This should be called periodically (e.g., via Celery task)

        Returns:
            Number of states cleaned up
        """
        query = delete(DialogState).where(
            DialogState.expires_at < datetime.now(timezone.utc)
        )
        result = await self.db.execute(query)
        await self.db.commit()

        count = result.rowcount
        if count > 0:
            logger.info(f"Cleaned up {count} expired dialog states")

        return count

