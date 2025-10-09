"""
Intent Service

Business logic layer for intent classification.
Handles caching, logging, and integration with the intent classifier.
"""

import logging
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from src.nlp.intent.classifier import IntentClassifier
from src.llm.gemini.client import LLMClient
from src.schemas.intent import (
    IntentClassificationRequest,
    IntentClassificationResponse,
    IntentResult
)

logger = logging.getLogger(__name__)


class IntentService:
    """
    Service class for intent classification business logic.
    
    Provides:
    - Multi-intent classification
    - Entity extraction
    - Caching (future)
    - Logging and metrics
    """
    
    def __init__(
        self,
        db: Optional[AsyncSession] = None,
        llm_client: Optional[LLMClient] = None
    ):
        """
        Initialize intent service
        
        Args:
            db: Database session (optional, for future caching)
            llm_client: LLM client (if None, will create one)
        """
        self.db = db
        self.llm_client = llm_client or LLMClient.create_for_intent_classification()
        self.classifier = IntentClassifier(llm_client=self.llm_client)
    
    async def classify_intent(
        self,
        request: IntentClassificationRequest
    ) -> IntentClassificationResponse:
        """
        Classify user message and detect all intents
        
        Args:
            request: Intent classification request
            
        Returns:
            IntentClassificationResponse with detected intents
        """
        start_time = datetime.now(timezone.utc)
        
        try:
            # Classify intent
            result, classification_method = await self.classifier.classify(request.message)
            
            # Calculate processing time
            end_time = datetime.now(timezone.utc)
            processing_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            # Build response
            response = IntentClassificationResponse(
                message=request.message,
                intents=result.intents,
                primary_intent=result.primary_intent,
                requires_clarification=result.requires_clarification,
                clarification_reason=result.clarification_reason,
                classification_method=classification_method,
                processing_time_ms=processing_time_ms
            )
            
            # Log classification
            logger.info(
                f"Intent classification completed: "
                f"primary_intent={result.primary_intent}, "
                f"method={classification_method}, "
                f"time={processing_time_ms}ms, "
                f"num_intents={len(result.intents)}"
            )
            
            # TODO: Store classification in database for analytics
            # TODO: Cache result for similar queries
            
            return response
            
        except Exception as e:
            logger.error(f"Error in intent classification: {e}", exc_info=True)
            
            # Return fallback response
            end_time = datetime.now(timezone.utc)
            processing_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            return IntentClassificationResponse(
                message=request.message,
                intents=[
                    IntentResult(
                        intent="unclear_intent",
                        confidence=0.0,
                        entities_json={}  # Changed from entities to entities_json
                    )
                ],
                primary_intent="unclear_intent",
                requires_clarification=True,
                clarification_reason=f"Classification error: {str(e)}",
                classification_method="error",
                processing_time_ms=processing_time_ms
            )
    
    async def classify_message(
        self,
        message: str,
        user_id: Optional[int] = None,
        session_id: Optional[str] = None
    ) -> IntentClassificationResponse:
        """
        Convenience method to classify a message directly
        
        Args:
            message: User message
            user_id: User ID (optional)
            session_id: Session ID (optional)
            
        Returns:
            IntentClassificationResponse
        """
        request = IntentClassificationRequest(
            message=message,
            user_id=user_id,
            session_id=session_id
        )
        
        return await self.classify_intent(request)
    
    def get_intent_description(self, intent: str) -> str:
        """
        Get human-readable description of an intent
        
        Args:
            intent: Intent name
            
        Returns:
            Intent description
        """
        from src.nlp.intent.config import INTENT_CONFIGS, IntentType
        
        try:
            intent_type = IntentType(intent)
            config = INTENT_CONFIGS.get(intent_type)
            return config.description if config else "Unknown intent"
        except ValueError:
            return "Unknown intent"
    
    def get_agent_for_intent(self, intent: str) -> str:
        """
        Get the agent that should handle a specific intent
        
        Args:
            intent: Intent name
            
        Returns:
            Agent name
        """
        from src.nlp.intent.config import INTENT_CONFIGS, IntentType
        
        try:
            intent_type = IntentType(intent)
            config = INTENT_CONFIGS.get(intent_type)
            return config.agent if config else "Coordinator"
        except ValueError:
            return "Coordinator"

