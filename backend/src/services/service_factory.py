"""
Service Factory

Centralized factory for creating service instances with all dependencies.
Creates new instances per request (no singletons for stateful services).
"""

import logging
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.slot_filling_service import SlotFillingService
from src.nlp.intent.classifier import IntentClassifier
from src.services.dialog_state_manager import DialogStateManager
from src.services.question_generator import QuestionGenerator
from src.services.entity_extractor import EntityExtractor
from src.services.entity_validator import EntityValidator
from src.nlp.llm.gemini_client import (
    get_gemini_client_for_classification,
    get_gemini_client_for_extraction
)

logger = logging.getLogger(__name__)


class SlotFillingServiceFactory:
    """
    Factory for creating slot-filling service with all dependencies
    
    Creates new instances per request to ensure thread safety and
    avoid shared mutable state between requests.
    """
    
    @staticmethod
    async def create(db: AsyncSession) -> SlotFillingService:
        """
        Create fully initialized slot-filling service
        
        Args:
            db: Database session
            
        Returns:
            SlotFillingService with all dependencies initialized
            
        Raises:
            Exception: If service initialization fails
        """
        try:
            logger.info("[ServiceFactory] Creating slot-filling service...")
            
            # 1. Initialize LLM clients (optimized for different tasks)
            classification_llm = get_gemini_client_for_classification()
            extraction_llm = get_gemini_client_for_extraction()
            
            logger.debug("[ServiceFactory] ✅ LLM clients initialized")
            
            # 2. Initialize intent classifier
            classifier = IntentClassifier(llm_client=classification_llm)
            logger.debug("[ServiceFactory] ✅ Intent classifier initialized")
            
            # 3. Initialize dialog state manager
            dialog_manager = DialogStateManager(db=db)
            logger.debug("[ServiceFactory] ✅ Dialog state manager initialized")
            
            # 4. Initialize question generator
            question_generator = QuestionGenerator()
            logger.debug("[ServiceFactory] ✅ Question generator initialized")
            
            # 5. Initialize entity extractor
            entity_extractor = EntityExtractor(llm_client=extraction_llm)
            logger.debug("[ServiceFactory] ✅ Entity extractor initialized")
            
            # 6. Initialize entity validator
            entity_validator = EntityValidator(db=db)
            logger.debug("[ServiceFactory] ✅ Entity validator initialized")
            
            # 7. Create slot-filling service
            slot_filling_service = SlotFillingService(
                db=db,
                classifier=classifier,
                dialog_manager=dialog_manager,
                question_generator=question_generator,
                entity_extractor=entity_extractor,
                entity_validator=entity_validator
            )
            
            logger.info("[ServiceFactory] ✅ Slot-filling service created successfully")
            return slot_filling_service
        
        except Exception as e:
            logger.error(f"[ServiceFactory] ❌ Failed to create slot-filling service: {e}", exc_info=True)
            raise


class ServiceFactory:
    """
    General service factory for future expansion
    
    Can be extended to create other service types as needed
    """
    
    @staticmethod
    async def create_slot_filling_service(db: AsyncSession) -> SlotFillingService:
        """
        Create slot-filling service
        
        Delegates to SlotFillingServiceFactory
        """
        return await SlotFillingServiceFactory.create(db)
    
    # Future: Add other service factories here
    # @staticmethod
    # async def create_agent_execution_service(db: AsyncSession) -> AgentExecutionService:
    #     ...
    #
    # @staticmethod
    # async def create_rag_service(db: AsyncSession) -> RAGService:
    #     ...

