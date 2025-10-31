"""
CoordinatorAgent - Orchestration Layer for Agent Routing

This agent serves as the central orchestrator that:
1. Receives user messages from the chat API
2. Classifies intent using the intent classification system
3. Routes requests to appropriate specialized agents
4. Manages conversation flow and context
5. Handles multi-turn conversations
6. Coordinates responses from multiple agents when needed
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.models import User, Conversation
from src.nlp.intent.classifier import IntentClassifier
from src.llm.gemini.client import LLMClient
from src.schemas.intent import IntentClassificationResult, IntentResult
from src.agents.policy.policy_agent import PolicyAgent
from src.agents.service.service_agent import ServiceAgent
from src.agents.booking.booking_agent import BookingAgent
from src.agents.cancellation.cancellation_agent import CancellationAgent
from src.agents.reschedule.reschedule_agent import RescheduleAgent
from src.agents.complaint.complaint_agent import ComplaintAgent
from src.agents.sql.sql_agent import SQLAgent


class CoordinatorAgent:
    """
    CoordinatorAgent orchestrates all specialized agents and manages conversation flow
    
    Responsibilities:
    - Intent classification and routing
    - Agent selection and execution
    - Conversation context management
    - Multi-turn conversation handling
    - Response coordination
    - Error handling and fallbacks
    """
    
    # Intent to Agent mapping
    INTENT_AGENT_MAP = {
        "greeting": "coordinator",  # Handle greetings in coordinator (simple, stateless)
        "policy_inquiry": "policy",
        "service_discovery": "service",
        "service_inquiry": "service",
        "service_information": "service",  # Route service information queries to ServiceAgent
        "booking_create": "booking",
        "booking_management": "booking",  # General booking intent
        "booking_modify": "booking",
        "booking_reschedule": "reschedule",  # Route to dedicated RescheduleAgent
        "booking_cancel": "cancellation",  # Route to dedicated CancellationAgent
        "booking_status": "booking",
        "complaint": "complaint",  # Route to ComplaintAgent
        "data_query": "sql",  # Route to SQLAgent for data queries
        "general_query": "coordinator",  # Handle general queries in coordinator
        "out_of_scope": "coordinator",  # Handle out-of-scope queries in coordinator
        "unclear_intent": "coordinator",  # Handle unclear intents in coordinator
    }
    
    def __init__(self, db: AsyncSession):
        """
        Initialize CoordinatorAgent

        Args:
            db: Database session for operations
        """
        self.db = db
        self.logger = logging.getLogger(__name__)

        # Initialize intent classifier
        try:
            self.llm_client = LLMClient.create_for_intent_classification()
            self.intent_classifier = IntentClassifier(llm_client=self.llm_client)

            # Lazy initialization: agents are created only when needed
            self._policy_agent = None
            self._service_agent = None
            self._booking_agent = None
            self._cancellation_agent = None
            self._reschedule_agent = None
            self._complaint_agent = None
            self._sql_agent = None

            self.logger.info("CoordinatorAgent initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing CoordinatorAgent: {e}")
            raise

    @property
    def policy_agent(self):
        """Lazy initialization of PolicyAgent"""
        if self._policy_agent is None:
            self.logger.info("Initializing PolicyAgent (lazy)")
            self._policy_agent = PolicyAgent(db=self.db)
        return self._policy_agent

    @property
    def service_agent(self):
        """Lazy initialization of ServiceAgent"""
        if self._service_agent is None:
            self.logger.info("Initializing ServiceAgent (lazy)")
            self._service_agent = ServiceAgent(db=self.db)
        return self._service_agent

    @property
    def booking_agent(self):
        """Lazy initialization of BookingAgent"""
        if self._booking_agent is None:
            self.logger.info("Initializing BookingAgent (lazy)")
            self._booking_agent = BookingAgent(db=self.db)
        return self._booking_agent

    @property
    def cancellation_agent(self):
        """Lazy initialization of CancellationAgent"""
        if self._cancellation_agent is None:
            self.logger.info("Initializing CancellationAgent (lazy)")
            self._cancellation_agent = CancellationAgent(db=self.db)
        return self._cancellation_agent

    @property
    def reschedule_agent(self):
        """Lazy initialization of RescheduleAgent"""
        if self._reschedule_agent is None:
            self.logger.info("Initializing RescheduleAgent (lazy)")
            self._reschedule_agent = RescheduleAgent(db=self.db)
        return self._reschedule_agent

    @property
    def complaint_agent(self):
        """Lazy initialization of ComplaintAgent"""
        if self._complaint_agent is None:
            self.logger.info("Initializing ComplaintAgent (lazy)")
            self._complaint_agent = ComplaintAgent(db=self.db)
        return self._complaint_agent

    @property
    def sql_agent(self):
        """Lazy initialization of SQLAgent"""
        if self._sql_agent is None:
            self.logger.info("Initializing SQLAgent (lazy)")
            self._sql_agent = SQLAgent(db=self.db)
        return self._sql_agent
    
    async def execute(
        self,
        message: str,
        user: User,
        session_id: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Main execution method for CoordinatorAgent with slot-filling support

        This method now uses the SlotFillingService to handle multi-turn conversations
        and collect required entities before executing agents.

        Args:
            message: User message
            user: User object
            session_id: Session ID for tracking
            conversation_history: Optional conversation history for context

        Returns:
            Dictionary with response, intent, agent_used, and metadata
        """
        try:
            # Extract user_id early to avoid lazy loading issues in async context
            user_id = user.id
            self.logger.info(f"CoordinatorAgent executing for user {user_id}, session: {session_id}")
            self.logger.info(f"Message: {message[:100]}...")

            # Check if there's an active dialog state (ongoing slot-filling or awaiting confirmation)
            from src.services.dialog_state_manager import DialogStateManager
            from src.core.models.dialog_state import DialogStateType
            dialog_manager = DialogStateManager(self.db)
            dialog_state = await dialog_manager.get_active_state(session_id)

            self.logger.info(f"[COORDINATOR] Dialog state: {dialog_state.state if dialog_state else 'None'}, Intent: {dialog_state.intent if dialog_state else 'None'}")

            # Handle confirmation responses (yes/no) for pending actions
            # Use an explicit None check and getattr to avoid evaluating SQLAlchemy ColumnElement truthiness
            if dialog_state is not None and getattr(dialog_state, "state", None) == DialogStateType.AWAITING_CONFIRMATION:
                self.logger.info(f"Handling confirmation response for pending action: {dialog_state.intent}")

                # Check if user confirmed or declined
                message_lower = message.lower().strip()
                confirmation_keywords = ['yes', 'yeah', 'yep', 'sure', 'ok', 'okay', 'correct', 'right', 'confirm']
                decline_keywords = ['no', 'nope', 'nah', 'not', 'cancel', 'wrong', 'dont']

                is_confirmed = any(keyword in message_lower for keyword in confirmation_keywords)
                is_declined = any(keyword in message_lower for keyword in decline_keywords)

                if is_confirmed:
                    # User confirmed - execute the pending action
                    pending_action = await dialog_manager.get_pending_action(session_id)

                    if pending_action:
                        action_type = pending_action.get("action_type")

                        if action_type == "cancel_booking":
                            # Execute confirmed cancellation
                            response = await self.cancellation_agent.execute_confirmed_cancellation(
                                pending_action=pending_action,
                                user=user,
                                session_id=session_id
                            )
                            response["agent_used"] = "cancellation"

                        elif action_type == "reschedule_booking":
                            # Execute confirmed reschedule
                            response = await self.reschedule_agent.execute_confirmed_reschedule(
                                pending_action=pending_action,
                                user=user,
                                session_id=session_id
                            )
                            response["agent_used"] = "reschedule"
                        else:
                            # Unknown action type
                            response = {
                                "response": "I'm sorry, I couldn't process your confirmation. Please try again.",
                                "action_taken": "unknown_action_type",
                                "agent_used": "coordinator"
                            }
                    else:
                        # No pending action found
                        response = {
                            "response": "I'm sorry, I couldn't find the action you're confirming. Please try again.",
                            "action_taken": "no_pending_action",
                            "agent_used": "coordinator"
                        }

                    # Store conversation
                    await self._store_conversation(
                        user_id=user_id,
                        session_id=session_id,
                        user_message=message,
                        assistant_response=response["response"],
                        intent=dialog_state.intent,
                        agent_used=response.get("agent_used", "unknown")
                    )

                    return {
                        "response": response["response"],
                        "intent": dialog_state.intent,
                        "confidence": 1.0,
                        "agent_used": response.get("agent_used", "unknown"),
                        "classification_method": "confirmation_handling",
                        "metadata": response.get("metadata", {})
                    }

                elif is_declined:
                    # User declined - clear pending action
                    await dialog_manager.clear_pending_action(session_id)

                    response_text = "Okay, I've cancelled that action. Is there anything else I can help you with?"

                    # Store conversation
                    await self._store_conversation(
                        user_id=user_id,
                        session_id=session_id,
                        user_message=message,
                        assistant_response=response_text,
                        intent=dialog_state.intent,
                        agent_used="coordinator"
                    )

                    return {
                        "response": response_text,
                        "intent": dialog_state.intent,
                        "confidence": 1.0,
                        "agent_used": "coordinator",
                        "classification_method": "confirmation_handling",
                        "metadata": {"action": "declined"}
                    }
                else:
                    # Unclear response - ask for clarification
                    response_text = "I didn't understand your response. Please reply with 'yes' to confirm or 'no' to cancel."

                    # Store conversation
                    await self._store_conversation(
                        user_id=user_id,
                        session_id=session_id,
                        user_message=message,
                        assistant_response=response_text,
                        intent=dialog_state.intent,
                        agent_used="coordinator"
                    )

                    return {
                        "response": response_text,
                        "intent": dialog_state.intent,
                        "confidence": 1.0,
                        "agent_used": "coordinator",
                        "classification_method": "confirmation_handling",
                        "metadata": {"action": "clarification_needed"}
                    }

            # If there's an active dialog state for slot-filling, use slot-filling service
            # Use explicit None check and getattr to avoid evaluating SQLAlchemy ColumnElement in boolean context
            if dialog_state is not None and getattr(dialog_state, "state", None) == DialogStateType.COLLECTING_INFO:
                self.logger.info(f"Active dialog state found: {getattr(dialog_state, 'intent', None)}, state: {getattr(dialog_state, 'state', None)}")
                from src.services.slot_filling_service import SlotFillingService
                from src.services.question_generator import QuestionGenerator
                from src.services.entity_extractor import EntityExtractor
                from src.services.entity_validator import EntityValidator

                # Initialize slot-filling service with all dependencies
                slot_filling_service = SlotFillingService(
                    db=self.db,
                    classifier=self.intent_classifier,
                    dialog_manager=dialog_manager,
                    question_generator=QuestionGenerator(),
                    entity_extractor=EntityExtractor(llm_client=self.llm_client),
                    entity_validator=EntityValidator(self.db)
                )

                # Process message through slot-filling
                result = await slot_filling_service.process_message(
                    user=user,
                    session_id=session_id,
                    message=message,
                    channel="web"
                )

                # Check if intent has changed (user is asking a different question)
                intent_changed = result.metadata.get("intent_changed", False)
                if intent_changed:
                    self.logger.info(f"Intent changed during slot-filling from {dialog_state.intent} to {result.metadata.get('intent')}")

                    # Clear the dialog state
                    await dialog_manager.clear_state(session_id)

                    # Re-classify and handle the new intent
                    intent_result, classification_method = await self.intent_classifier.classify(
                        message=message,
                        conversation_history=conversation_history
                    )

                    # Get primary intent details
                    primary_intent_obj = intent_result.intents[0]

                    # Route to appropriate agent
                    response = await self._route_to_agent(
                        intent_result=primary_intent_obj,
                        user=user,
                        session_id=session_id,
                        message=message,
                        conversation_history=conversation_history
                    )

                    # Store conversation
                    await self._store_conversation(
                        user_id=user_id,
                        session_id=session_id,
                        user_message=message,
                        assistant_response=response["response"],
                        intent=intent_result.primary_intent,
                        agent_used=response.get("agent_used", "unknown")
                    )

                    return {
                        "response": response["response"],
                        "intent": intent_result.primary_intent,
                        "confidence": primary_intent_obj.confidence,
                        "agent_used": response.get("agent_used", "unknown"),
                        "classification_method": classification_method,
                        "metadata": response.get("metadata", {})
                    }

                # If slot-filling is complete, execute the agent
                if result.should_trigger_agent:
                    self.logger.info(f"Slot-filling complete, executing agent with entities: {result.collected_entities}")

                    # Map entity names to match agent expectations
                    # LLM may extract 'zip_code' but agents expect 'location'
                    mapped_entities = result.collected_entities.copy()
                    if 'zip_code' in mapped_entities and 'location' not in mapped_entities:
                        mapped_entities['location'] = mapped_entities.pop('zip_code')
                        self.logger.info(f"Mapped 'zip_code' to 'location': {mapped_entities.get('location')}")

                    # Add dialog state context to entities for agent use
                    # This includes rate_card_id from service subcategory validation
                    # Note: DialogState model uses 'context' field, not 'metadata'
                    if dialog_state.context:
                        try:
                            # Handle both dict and JSON string
                            if isinstance(dialog_state.context, dict):
                                context_dict = dialog_state.context
                            else:
                                # If it's a string (JSON), parse it
                                import json
                                context_dict = json.loads(str(dialog_state.context))

                            # Add context items to entities with _metadata_ prefix
                            for key, value in context_dict.items():
                                # Skip non-metadata fields like available_subcategories
                                if key in ['available_subcategories', 'service_type']:
                                    continue
                                if key not in mapped_entities:  # Don't override existing entities
                                    mapped_entities[f"_metadata_{key}"] = value
                                    self.logger.info(f"Added context to entities: _metadata_{key} = {value}")
                        except Exception as e:
                            self.logger.warning(f"Could not process dialog state context: {e}")
                            # Continue without context

                    # Also check collected_entities for metadata fields (stored during validation)
                    if dialog_state.collected_entities:
                        try:
                            if isinstance(dialog_state.collected_entities, dict):
                                collected_dict = dialog_state.collected_entities
                            else:
                                import json
                                collected_dict = json.loads(str(dialog_state.collected_entities))

                            # Copy metadata fields from collected_entities
                            for key, value in collected_dict.items():
                                if key.startswith('_metadata_'):
                                    mapped_entities[key] = value
                                    self.logger.info(f"Added metadata from collected_entities: {key} = {value}")
                        except Exception as e:
                            self.logger.warning(f"Could not process collected_entities for metadata: {e}")

                    # Create IntentResult with collected entities
                    from src.schemas.intent import IntentResult as IntentResultClass
                    intent_result_for_agent = IntentResultClass(
                        intent=dialog_state.intent,
                        entities_json=mapped_entities,  # Pass as entities_json, validator will convert dict to JSON string
                        confidence=result.metadata.get("intent_confidence", 0.95)
                    )

                    # Execute the agent with collected entities
                    agent_response = await self._route_to_agent(
                        intent_result=intent_result_for_agent,
                        user=user,
                        session_id=session_id,
                        message=message,
                        conversation_history=conversation_history
                    )

                    # Clear the dialog state ONLY if the agent response doesn't require confirmation
                    # If requires_confirmation is True, the dialog state should be kept for confirmation handling
                    if not agent_response.get("requires_confirmation", False):
                        await dialog_manager.clear_state(session_id)
                        self.logger.info(f"[COORDINATOR] Cleared dialog state after agent execution (no confirmation required)")
                    else:
                        self.logger.info(f"[COORDINATOR] Keeping dialog state for confirmation (requires_confirmation=True)")

                    # Store conversation
                    await self._store_conversation(
                        user_id=user_id,
                        session_id=session_id,
                        user_message=message,
                        assistant_response=agent_response["response"],
                        intent=dialog_state.intent,
                        agent_used=agent_response.get("agent_used", "unknown")
                    )

                    return {
                        "response": agent_response["response"],
                        "intent": dialog_state.intent,
                        "confidence": result.metadata.get("intent_confidence", 0.95),
                        "agent_used": agent_response.get("agent_used", "unknown"),
                        "classification_method": "slot_filling",
                        "metadata": {
                            **agent_response.get("metadata", {}),
                            **result.metadata
                        }
                    }
                else:
                    # Still collecting entities, return the question
                    # Store conversation
                    await self._store_conversation(
                        user_id=user_id,
                        session_id=session_id,
                        user_message=message,
                        assistant_response=result.final_response,
                        intent=dialog_state.intent,
                        agent_used="slot_filling"
                    )

                    return {
                        "response": result.final_response,
                        "intent": dialog_state.intent,
                        "confidence": result.metadata.get("intent_confidence", 0.95),
                        "agent_used": "slot_filling",
                        "classification_method": "slot_filling",
                        "metadata": result.metadata
                    }

            # No active dialog state - classify intent and check if slot-filling is needed
            # Step 1: Classify intent
            intent_result, classification_method = await self.intent_classifier.classify(
                message=message,
                conversation_history=conversation_history
            )

            # Get primary intent details
            primary_intent_obj = intent_result.intents[0]  # First intent is primary

            self.logger.info(f"Intent classification: {intent_result.primary_intent} "
                           f"(confidence: {primary_intent_obj.confidence:.2f}, "
                           f"method: {classification_method})")

            # Step 2: Check if this intent requires slot-filling
            from src.nlp.intent.config import INTENT_CONFIGS, IntentType
            intent_type = IntentType(intent_result.primary_intent)
            intent_config = INTENT_CONFIGS.get(intent_type)

            # If intent requires entities and not all are collected, start slot-filling
            if intent_config and (intent_config.required_entities or intent_config.optional_entities):
                collected_entities = primary_intent_obj.entities
                required_entities = [e.value for e in intent_config.required_entities]

                # Special handling for booking_management: always start slot-filling
                # because required entities depend on the action (book/cancel/reschedule/modify)
                if intent_result.primary_intent == "booking_management":
                    action = collected_entities.get("action", "book")

                    self.logger.info(f"[COORDINATOR] booking_management detected, action={action}")
                    self.logger.info(f"[COORDINATOR] collected_entities={collected_entities}")

                    # Determine actual required entities based on action
                    # Order matters: location first (to check availability), then date/time
                    if action == "book":
                        required_entities = ["service_type", "location", "date", "time"]
                    elif action == "cancel":
                        # For cancel: either booking_id OR booking_filter (latest/recent/last) is required
                        # If booking_filter is present, we don't need booking_id
                        if "booking_filter" in collected_entities or "service_type" in collected_entities:
                            required_entities = []  # booking_filter or service_type is enough to identify booking
                        else:
                            required_entities = ["booking_id"]
                    elif action == "reschedule":
                        # For reschedule: either booking_id OR booking_filter is required, plus new date/time
                        if "booking_filter" in collected_entities or "service_type" in collected_entities:
                            required_entities = ["new_date", "new_time"]  # booking_filter or service_type is enough
                        else:
                            required_entities = ["booking_id", "new_date", "new_time"]
                    elif action == "modify":
                        # For modify: either booking_id OR booking_filter is required
                        if "booking_filter" in collected_entities or "service_type" in collected_entities:
                            required_entities = []  # booking_filter or service_type is enough
                        else:
                            required_entities = ["booking_id"]

                    self.logger.info(f"[COORDINATOR] booking_management action={action}, required_entities={required_entities}")

                    # Calculate missing entities
                    missing_entities = [e for e in required_entities if e not in collected_entities]

                    # Special check: if service_type is present, check if it requires subcategory selection
                    # This ensures we start slot-filling even when all entities are present
                    needs_subcategory_validation = False
                    if "service_type" in collected_entities and action == "book":
                        service_type = collected_entities.get("service_type", "").lower()
                        self.logger.info(f"[COORDINATOR] Checking service_type='{service_type}' for subcategory validation")

                        # Normalize service variations to match services_requiring_subcategory keys
                        service_normalizations = {
                            # Home Cleaning variations
                            "cleaning": "home_cleaning",
                            "house cleaning": "home_cleaning",
                            "home cleaning": "home_cleaning",
                            "cleaning service": "home_cleaning",

                            # Appliance Repair variations
                            "appliance": "appliance_repair",
                            "appliance repair": "appliance_repair",
                            "appliance service": "appliance_repair",

                            # Plumbing variations
                            "plumbing": "plumbing",
                            "plumbing service": "plumbing",
                            "plumber": "plumbing",

                            # Electrical variations
                            "electrical": "electrical",
                            "electrical service": "electrical",
                            "electrician": "electrical",

                            # Carpentry variations
                            "carpentry": "carpentry",
                            "carpentry service": "carpentry",
                            "carpenter": "carpentry",
                            "furniture": "carpentry",

                            # Painting variations
                            "painting": "painting",
                            "painting service": "painting",
                            "paint": "painting",
                            "painter": "painting",
                            "interior painting": "painting",
                            "exterior painting": "painting",
                            "wall painting": "painting",

                            # Pest Control variations
                            "pest": "pest_control",
                            "pest control": "pest_control",
                            "pest control service": "pest_control",
                            "general pest control": "pest_control",

                            # Water Purifier variations
                            "water purifier": "water_purifier",
                            "water purifier service": "water_purifier",
                            "ro": "water_purifier",
                            "ro service": "water_purifier",

                            # Car Care variations
                            "car": "car_care",
                            "car care": "car_care",
                            "car service": "car_care",
                            "car wash": "car_care",
                            "car cleaning": "car_care",

                            # Salon variations
                            "salon": "salon_for_women",  # Default to women
                            "salon for women": "salon_for_women",
                            "women salon": "salon_for_women",
                            "salon for men": "salon_for_men",
                            "men salon": "salon_for_men",
                            "beauty": "salon_for_women",
                            "grooming": "salon_for_men",

                            # Packers and Movers variations
                            "packers": "packers_and_movers",
                            "movers": "packers_and_movers",
                            "packers and movers": "packers_and_movers",
                            "packing": "packers_and_movers",
                            "moving": "packers_and_movers",
                            "relocation": "packers_and_movers"
                        }
                        normalized_service = service_normalizations.get(service_type, service_type)
                        self.logger.info(f"[COORDINATOR] Normalized service: '{service_type}' -> '{normalized_service}'")

                        # Services that require subcategory selection (all multi-option services)
                        # Use normalized service names only
                        services_requiring_subcategory = {
                            "home_cleaning", "appliance_repair", "plumbing", "electrical",
                            "carpentry", "painting", "pest_control", "water_purifier",
                            "car_care", "salon_for_women", "salon_for_men", "packers_and_movers"
                        }

                        if normalized_service in services_requiring_subcategory:
                            needs_subcategory_validation = True
                            self.logger.info(f"[COORDINATOR] ✅ Service '{service_type}' (normalized: '{normalized_service}') requires subcategory selection")
                        else:
                            self.logger.info(f"[COORDINATOR] ❌ Service '{service_type}' (normalized: '{normalized_service}') does NOT require subcategory selection")

                    # Check if slot-filling is needed for booking_management
                    if missing_entities or needs_subcategory_validation:
                        if missing_entities:
                            self.logger.info(f"Missing entities: {missing_entities}, starting slot-filling")
                        if needs_subcategory_validation:
                            self.logger.info(f"Service requires subcategory selection, starting slot-filling")

                        # Create dialog state for this session
                        from src.schemas.dialog_state import DialogStateCreate
                        from src.core.models.dialog_state import DialogStateType

                        # IMPORTANT: Only include entities that don't need validation/normalization
                        # Entities like date, time need to be validated by the slot-filling graph
                        # Safe entities: action, service_type, booking_id, status_filter, sort_by, location (if from address)
                        entities_needing_validation = {'date', 'time'}
                        safe_entities = {k: v for k, v in collected_entities.items() if k not in entities_needing_validation}

                        self.logger.info(f"Safe entities for dialog state: {safe_entities}")

                        dialog_state_data = DialogStateCreate(
                            session_id=session_id,
                            user_id=user_id,
                            intent=intent_result.primary_intent,
                            state=DialogStateType.COLLECTING_INFO,
                            collected_entities=safe_entities,  # Only include safe entities
                            needed_entities=missing_entities,
                            channel="web"
                        )

                        await dialog_manager.create_state(dialog_state_data)
                        self.logger.info(f"Created dialog state for session {session_id}")

                        from src.services.slot_filling_service import SlotFillingService
                        from src.services.question_generator import QuestionGenerator
                        from src.services.entity_extractor import EntityExtractor
                        from src.services.entity_validator import EntityValidator

                        # Initialize slot-filling service with all dependencies
                        slot_filling_service = SlotFillingService(
                            db=self.db,
                            classifier=self.intent_classifier,
                            dialog_manager=dialog_manager,
                            question_generator=QuestionGenerator(),
                            entity_extractor=EntityExtractor(llm_client=self.llm_client),
                            entity_validator=EntityValidator(self.db)
                        )

                        # Start slot-filling process
                        result = await slot_filling_service.process_message(
                            user=user,
                            session_id=session_id,
                            message=message,
                            channel="web"
                        )

                        # Store conversation
                        await self._store_conversation(
                            user_id=user_id,
                            session_id=session_id,
                            user_message=message,
                            assistant_response=result.final_response,
                            intent=intent_result.primary_intent,
                            agent_used="slot_filling"
                        )

                        return {
                            "response": result.final_response,
                            "intent": intent_result.primary_intent,
                            "confidence": primary_intent_obj.confidence,
                            "agent_used": "slot_filling",
                            "classification_method": classification_method,
                            "metadata": result.metadata
                        }
                else:
                    # For non-booking intents: only check for missing required entities
                    # No subcategory validation needed for service_information, etc.
                    missing_entities = [e for e in required_entities if e not in collected_entities]

                    if missing_entities:
                        self.logger.info(f"Missing entities for {intent_result.primary_intent}: {missing_entities}, starting slot-filling")

                        # Create dialog state for this session
                        from src.schemas.dialog_state import DialogStateCreate
                        from src.core.models.dialog_state import DialogStateType

                        # Only include entities that don't need validation/normalization
                        entities_needing_validation = {'date', 'time'}
                        safe_entities = {k: v for k, v in collected_entities.items() if k not in entities_needing_validation}

                        self.logger.info(f"Safe entities for dialog state: {safe_entities}")

                        dialog_state_data = DialogStateCreate(
                            session_id=session_id,
                            user_id=user_id,
                            intent=intent_result.primary_intent,
                            state=DialogStateType.COLLECTING_INFO,
                            collected_entities=safe_entities,
                            needed_entities=missing_entities,
                            channel="web"
                        )

                        await dialog_manager.create_state(dialog_state_data)
                        self.logger.info(f"Created dialog state for session {session_id}")

                        from src.services.slot_filling_service import SlotFillingService
                        from src.services.question_generator import QuestionGenerator
                        from src.services.entity_extractor import EntityExtractor
                        from src.services.entity_validator import EntityValidator

                        # Initialize slot-filling service with all dependencies
                        slot_filling_service = SlotFillingService(
                            db=self.db,
                            classifier=self.intent_classifier,
                            dialog_manager=dialog_manager,
                            question_generator=QuestionGenerator(),
                            entity_extractor=EntityExtractor(llm_client=self.llm_client),
                            entity_validator=EntityValidator(self.db)
                        )

                        # Start slot-filling process
                        result = await slot_filling_service.process_message(
                            user=user,
                            session_id=session_id,
                            message=message,
                            channel="web"
                        )

                        # Store conversation
                        await self._store_conversation(
                            user_id=user_id,
                            session_id=session_id,
                            user_message=message,
                            assistant_response=result.final_response,
                            intent=intent_result.primary_intent,
                            agent_used="slot_filling"
                        )

                        return {
                            "response": result.final_response,
                            "intent": intent_result.primary_intent,
                            "confidence": primary_intent_obj.confidence,
                            "agent_used": "slot_filling",
                            "classification_method": classification_method,
                            "metadata": result.metadata
                        }

            # Step 3: All entities collected or no entities needed - route to agent
            if len(intent_result.intents) == 1:
                # Single intent - route to one agent
                response = await self._route_to_agent(
                    intent_result=primary_intent_obj,
                    user=user,
                    session_id=session_id,
                    message=message,  # Pass original message for agents that need it
                    conversation_history=conversation_history
                )
            else:
                # Multiple intents - handle sequentially
                response = await self._handle_multi_intent(
                    intent_result=intent_result,
                    user=user,
                    session_id=session_id,
                    message=message  # Pass original message for agents that need it
                )

            # Step 4: Store conversation (both user message and assistant response)
            await self._store_conversation(
                user_id=user_id,
                session_id=session_id,
                user_message=message,
                assistant_response=response["response"],
                intent=intent_result.primary_intent,  # primary_intent is now a string
                agent_used=response.get("agent_used", "unknown")
            )

            # Step 5: Return coordinated response
            return {
                "response": response["response"],
                "intent": intent_result.primary_intent,
                "confidence": primary_intent_obj.confidence,
                "agent_used": response.get("agent_used", "unknown"),
                "classification_method": classification_method,
                "metadata": {
                    **response.get("metadata", {}),
                    "all_intents": [
                        {"intent": i.intent, "confidence": i.confidence}
                        for i in intent_result.intents
                    ]
                }
            }

        except Exception as e:
            self.logger.error(f"Error in CoordinatorAgent execution: {e}", exc_info=True)
            return {
                "response": "I apologize, but I encountered an error processing your request. Please try again or contact support if the issue persists.",
                "intent": "error",
                "confidence": 0.0,
                "agent_used": "none",
                "classification_method": "error",
                "metadata": {"error": str(e)}
            }
    
    async def _route_to_agent(
        self,
        intent_result: IntentResult,
        user: User,
        session_id: str,
        message: str = "",  # Original message for agents that need it
        conversation_history: Optional[List[Dict[str, str]]] = None  # Conversation history for context
    ) -> Dict[str, Any]:
        """
        Route request to appropriate specialized agent

        Args:
            intent_result: Classified intent with entities
            user: User object
            session_id: Session ID
            message: Original user message (for agents that need full context)
            conversation_history: Conversation history for context-aware responses

        Returns:
            Agent response dictionary
        """
        intent = intent_result.intent
        entities = intent_result.entities

        # Determine which agent to use
        agent_type = self.INTENT_AGENT_MAP.get(intent, "policy")

        # Special handling for booking_management: route based on action
        if intent == "booking_management":
            action = entities.get("action", "book")
            if action == "cancel":
                agent_type = "cancellation"
                self.logger.info(f"Routing booking_management with action=cancel to cancellation agent")
            elif action == "reschedule":
                agent_type = "reschedule"
                self.logger.info(f"Routing booking_management with action=reschedule to reschedule agent")
            else:
                # book, modify, list, etc. go to booking agent
                agent_type = "booking"
                self.logger.info(f"Routing booking_management with action={action} to booking agent")
        else:
            self.logger.info(f"Routing intent '{intent}' to {agent_type} agent")

        try:
            # Handle coordinator-level intents (greetings, general queries, out-of-scope, unclear)
            if agent_type == "coordinator":
                if intent == "greeting":
                    return await self._handle_greeting(user, message, conversation_history)
                elif intent == "general_query":
                    return await self._handle_general_query(user, message, conversation_history)
                elif intent == "out_of_scope":
                    return await self._handle_out_of_scope(user, message, conversation_history)
                elif intent == "unclear_intent":
                    return await self._handle_unclear_intent(user, message, conversation_history)
                else:
                    # Unknown coordinator intent, fallback to policy
                    self.logger.warning(f"Unknown coordinator intent '{intent}', falling back to policy agent")
                    agent_type = "policy"

            if agent_type == "policy":
                response = await self.policy_agent.execute(
                    intent=intent,
                    entities=entities,
                    user=user,
                    session_id=session_id,
                    message=message  # Pass original message for RAG query
                )
                response["agent_used"] = "policy"
                
            elif agent_type == "service":
                response = await self.service_agent.execute(
                    intent=intent,
                    entities=entities,
                    user=user,
                    session_id=session_id,
                    message=message  # Pass original message for smart inference
                )
                response["agent_used"] = "service"
                
            elif agent_type == "booking":
                response = await self.booking_agent.execute(
                    intent=intent,
                    entities=entities,
                    user=user,
                    session_id=session_id
                )
                response["agent_used"] = "booking"

            elif agent_type == "cancellation":
                response = await self.cancellation_agent.execute(
                    message=message,  # Pass message for fallback entity extraction
                    user=user,
                    session_id=session_id,
                    entities=entities
                )
                response["agent_used"] = "cancellation"

            elif agent_type == "reschedule":
                response = await self.reschedule_agent.execute(
                    message=message,  # Pass message for fallback entity extraction
                    user=user,
                    session_id=session_id,
                    entities=entities
                )
                response["agent_used"] = "reschedule"

            elif agent_type == "complaint":
                response = await self.complaint_agent.execute(
                    message=message,  # Full message needed for complaint
                    user=user,
                    session_id=session_id,
                    entities=entities
                )
                response["agent_used"] = "complaint"

            elif agent_type == "sql":
                response = await self.sql_agent.execute(
                    message=message,  # Full message needed for SQL generation
                    user=user,
                    session_id=session_id,
                    entities=entities
                )
                response["agent_used"] = "sql"

            else:
                # Fallback to policy agent for unknown intents
                self.logger.warning(f"Unknown agent type '{agent_type}', falling back to policy agent")
                response = await self.policy_agent.execute(
                    intent=intent,
                    entities=entities,
                    user=user,
                    session_id=session_id,
                    message=message  # Pass original message for RAG query
                )
                response["agent_used"] = "policy_fallback"
            
            return response

        except Exception as e:
            self.logger.error(f"Error routing to {agent_type} agent: {e}", exc_info=True)
            return {
                "response": f"I encountered an error while processing your {intent} request. Please try again.",
                "action_taken": "error",
                "agent_used": f"{agent_type}_error",
                "metadata": {"error": str(e)}
            }

    async def _handle_greeting(
        self,
        user: User,
        message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Handle greeting intent using LLM for natural, context-aware responses

        Args:
            user: User object
            message: Original greeting message
            conversation_history: Previous conversation for context

        Returns:
            Greeting response dictionary
        """
        user_name = user.first_name or "there"

        # Use LLM to generate a natural, context-aware greeting
        from src.llm.gemini.prompts import get_system_prompt

        # Build context-aware prompt
        context_info = ""
        if conversation_history and len(conversation_history) > 0:
            context_info = f"\n\nPrevious conversation context: The user has interacted with you before."

        prompt = f"""The user said: "{message}"

Generate a warm, friendly greeting response that:
1. Greets the user by name: {user_name}
2. Introduces yourself as Lisa, their ConvergeAI assistant
3. Briefly mentions you can help with home services (AC repair, plumbing, cleaning, electrical, etc.)
4. Asks how you can help them today
5. Keeps it natural and conversational (2-3 sentences)
{context_info}

Remember: Be friendly, not robotic. No emojis, no bullet points, no structured formatting."""

        try:
            response_text = await self.llm_client.generate(
                prompt=prompt,
                system_prompt=get_system_prompt("conversational_response"),
                temperature=0.7
            )

            self.logger.info(f"Generated LLM greeting for user {user.id}")

        except Exception as e:
            self.logger.error(f"Error generating greeting response: {e}")
            # Fallback response (only used if LLM fails)
            response_text = (
                f"Hi {user_name}! I'm Lisa, your ConvergeAI assistant. "
                f"I can help you book home services like AC repair, plumbing, cleaning, and more. "
                f"What can I do for you today?"
            )

        return {
            "response": response_text,
            "action_taken": "greeting_handled",
            "agent_used": "coordinator",
            "metadata": {
                "user_name": user_name,
                "greeting_message": message,
                "llm_generated": True
            }
        }

    async def _handle_general_query(
        self,
        user: User,
        message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Handle general query intent using LLM for natural, context-aware responses

        Args:
            user: User object
            message: Original query message
            conversation_history: Previous conversation for context

        Returns:
            General query response dictionary
        """
        user_name = user.first_name or "there"

        # Use LLM to generate a natural, context-aware response
        from src.llm.gemini.prompts import get_system_prompt

        # Build context-aware prompt
        context_info = ""
        if conversation_history and len(conversation_history) > 0:
            recent_history = conversation_history[-3:] if len(conversation_history) > 3 else conversation_history
            context_info = "\n\nRecent conversation:\n"
            for msg in recent_history:
                role = msg.get("role", "unknown").capitalize()
                content = msg.get("content", "")
                context_info += f"{role}: {content}\n"

        prompt = f"""The user asked: "{message}"

This is a general query. Generate a warm, helpful response that:
1. Acknowledges their question
2. Explains what you can help with (booking services, checking prices, managing bookings, answering policy questions)
3. Offers to assist them
4. Keeps it natural and conversational (2-3 sentences)
5. Uses the user's name: {user_name}
{context_info}

Remember: Be friendly and helpful, not robotic. No emojis, no bullet points, no structured formatting."""

        try:
            response_text = await self.llm_client.generate(
                prompt=prompt,
                system_prompt=get_system_prompt("conversational_response"),
                temperature=0.7
            )

            self.logger.info(f"Generated LLM general query response for user {user.id}")

        except Exception as e:
            self.logger.error(f"Error generating general query response: {e}")
            # Fallback response (only used if LLM fails)
            response_text = (
                f"I'm here to help, {user_name}! I can assist you with booking home services, "
                f"checking prices and availability, managing your bookings, and answering policy questions. "
                f"What would you like to know?"
            )

        return {
            "response": response_text,
            "action_taken": "general_query_handled",
            "agent_used": "coordinator",
            "metadata": {
                "query": message,
                "llm_generated": True
            }
        }

    async def _handle_out_of_scope(
        self,
        user: User,
        message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Handle out-of-scope queries using LLM to generate natural responses

        Out-of-scope queries are those outside the home services domain
        (e.g., weather, news, sports, jokes, travel bookings, etc.)

        Args:
            user: User object
            message: Original out-of-scope query

        Returns:
            Out-of-scope response dictionary
        """
        user_name = user.first_name or "there"

        # Use LLM to generate a natural, context-aware response
        from src.llm.gemini.prompts import get_system_prompt

        prompt = f"""The user asked: "{message}"

This query is outside the scope of home services. Generate a warm, friendly response that:
1. Politely acknowledges their query
2. Explains you focus on home services (AC repair, plumbing, cleaning, electrical, etc.)
3. Offers to help with home services instead
4. Keeps it natural and conversational (2-3 sentences)
5. Uses the user's name: {user_name}

Remember: Be friendly, not robotic. No emojis, no bullet points, no structured formatting."""

        try:
            response_text = await self.llm_client.generate(
                prompt=prompt,
                system_prompt=get_system_prompt("conversational_response"),
                temperature=0.7
            )

            self.logger.info(f"Handled out-of-scope query for user {user.id}: {message[:50]}...")

        except Exception as e:
            self.logger.error(f"Error generating out-of-scope response: {e}")
            # Fallback response (only used if LLM fails)
            response_text = (
                f"I appreciate you reaching out, {user_name}! I specialize in home services like "
                f"AC repair, plumbing, and cleaning. Is there a home service I can help you with today?"
            )

        return {
            "response": response_text,
            "action_taken": "out_of_scope_handled",
            "agent_used": "coordinator",
            "metadata": {
                "query": message,
                "reason": "query_outside_home_services_scope"
            }
        }

    async def _handle_unclear_intent(
        self,
        user: User,
        message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Handle unclear intents using LLM to generate natural clarification requests

        Unclear intents are ambiguous queries where the user's intention is not clear.

        Args:
            user: User object
            message: Original unclear message

        Returns:
            Clarification response dictionary
        """
        user_name = user.first_name or "there"

        # Use LLM to generate a natural, context-aware clarification request
        from src.llm.gemini.prompts import get_system_prompt

        prompt = f"""The user said: "{message}"

Their intent is unclear. Generate a warm, friendly response that:
1. Acknowledges their message
2. Asks for clarification in a natural way
3. Optionally suggests what you can help with (booking services, checking prices, managing bookings, etc.)
4. Keeps it conversational (2-3 sentences)
5. Uses the user's name: {user_name}

Remember: Be friendly and helpful, not robotic. No emojis, no bullet points, no structured formatting."""

        try:
            response_text = await self.llm_client.generate(
                prompt=prompt,
                system_prompt=get_system_prompt("conversational_response"),
                temperature=0.7
            )

            self.logger.info(f"Handled unclear intent for user {user.id}: {message[:50]}...")

        except Exception as e:
            self.logger.error(f"Error generating unclear intent response: {e}")
            # Fallback response (only used if LLM fails)
            response_text = (
                f"I want to help you, {user_name}, but I'm not quite sure what you need. "
                f"Could you tell me a bit more? I can help with booking services, checking prices, "
                f"or managing your bookings."
            )

        return {
            "response": response_text,
            "action_taken": "unclear_intent_handled",
            "agent_used": "coordinator",
            "metadata": {
                "query": message,
                "reason": "intent_unclear_needs_clarification"
            }
        }

    async def _route_to_agent_with_timing(
        self,
        intent_result: IntentResult,
        user: User,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Route to agent with execution time tracking

        Args:
            intent_result: Single intent result
            user: User object
            session_id: Session ID

        Returns:
            Agent response with execution time
        """
        start_time = datetime.utcnow()

        try:
            response = await self._route_to_agent(
                intent_result=intent_result,
                user=user,
                session_id=session_id,
                conversation_history=None  # No conversation history in timing wrapper
            )

            end_time = datetime.utcnow()
            execution_time_ms = int((end_time - start_time).total_seconds() * 1000)

            # Add execution time to response
            response["execution_time_ms"] = execution_time_ms

            return response

        except Exception as e:
            end_time = datetime.utcnow()
            execution_time_ms = int((end_time - start_time).total_seconds() * 1000)

            self.logger.error(f"Error in _route_to_agent_with_timing: {e}")
            return {
                "response": f"Error processing {intent_result.intent}",
                "action_taken": "error",
                "agent_used": "error",
                "error": str(e),
                "execution_time_ms": execution_time_ms
            }

    async def _handle_multi_intent(
        self,
        intent_result: IntentClassificationResult,
        user: User,
        session_id: str,
        message: str = ""  # Original message for agents that need it
    ) -> Dict[str, Any]:
        """
        Handle requests with multiple intents using parallel execution

        Uses the Agent Execution Graph for:
        - Parallel execution of independent intents
        - Sequential execution of dependent intents
        - Response merging with provenance tracking

        Args:
            intent_result: Classification result with multiple intents
            user: User object
            session_id: Session ID
            message: Original user message (for agents that need full context)

        Returns:
            Coordinated response from multiple agents with provenance
        """
        self.logger.info(f"Handling multi-intent request with {len(intent_result.intents)} intents")

        try:
            # Extract user_id early to avoid lazy loading issues
            user_id = user.id

            # Import here to avoid circular dependency
            from src.graphs.agent_execution_graph import create_agent_execution_graph

            # Create agent execution graph
            graph = create_agent_execution_graph(self)

            # Prepare initial state (use user_id extracted earlier)
            initial_state = {
                "user": user,
                "user_id": user_id,  # Use pre-extracted user_id to avoid lazy loading
                "session_id": session_id,
                "intent_result": intent_result.model_dump(),
                "agent_timeout": 30,  # 30 seconds timeout
                "metadata": {
                    "graph_name": "agent_execution",
                    "nodes_executed": []
                }
            }

            # Execute graph
            result = await graph.ainvoke(initial_state)

            # Check for errors
            if result.get("error"):
                error = result["error"]
                self.logger.error(f"Agent execution graph error: {error}")
                return {
                    "response": "I encountered an error processing your request. Please try again.",
                    "action_taken": "error",
                    "agent_used": "coordinator",
                    "metadata": {"error": error}
                }

            # Return merged response with provenance
            return {
                "response": result.get("final_response", ""),
                "action_taken": "multi_intent_handled",
                "agent_used": "multi_agent",
                "provenance": result.get("provenance", []),
                "metadata": {
                    "intent_count": len(intent_result.intents),
                    "intents_processed": [i.intent for i in intent_result.intents],
                    "agents_used": result.get("agents_used", []),
                    "execution_plan": result.get("execution_plan"),
                    "combined_metadata": result.get("combined_metadata", {}),
                    "graph_metadata": result.get("metadata", {})
                }
            }

        except Exception as e:
            self.logger.error(f"Error in _handle_multi_intent: {e}", exc_info=True)

            # Fallback to sequential execution
            self.logger.info("Falling back to sequential execution")
            return await self._handle_multi_intent_fallback(intent_result, user, session_id)

    async def _handle_multi_intent_fallback(
        self,
        intent_result: IntentClassificationResult,
        user: User,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Fallback method for multi-intent handling (sequential execution)

        Used when the agent execution graph fails.

        Args:
            intent_result: Classification result with multiple intents
            user: User object
            session_id: Session ID

        Returns:
            Coordinated response from multiple agents
        """
        responses = []
        agents_used = []

        # Execute each intent sequentially
        for intent in intent_result.intents:
            try:
                response = await self._route_to_agent(
                    intent_result=intent,
                    user=user,
                    session_id=session_id,
                    message=message,  # Pass original message
                    conversation_history=None  # No conversation history in fallback
                )
                responses.append(response["response"])
                agents_used.append(response.get("agent_used", "unknown"))
            except Exception as e:
                self.logger.error(f"Error handling intent {intent.intent}: {e}")
                responses.append(f"I had trouble processing part of your request ({intent.intent}).")

        # Combine responses
        combined_response = "\n\n".join(responses)

        return {
            "response": combined_response,
            "action_taken": "multi_intent_handled_fallback",
            "agent_used": ", ".join(agents_used),
            "metadata": {
                "intent_count": len(intent_result.intents),
                "intents_processed": [i.intent for i in intent_result.intents],
                "fallback_used": True
            }
        }
    
    async def _store_conversation(
        self,
        user_id: int,
        session_id: str,
        user_message: str,
        assistant_response: str,
        intent: str,
        agent_used: str
    ):
        """
        Store conversation in database (both user message and assistant response)

        Args:
            user_id: User ID
            session_id: Session ID
            user_message: User's message
            assistant_response: Assistant's response
            intent: Classified intent
            agent_used: Agent that handled the request
        """
        try:
            # Import MessageRole enum
            from src.core.models.conversation import MessageRole

            # Store user message
            user_conv = Conversation(
                user_id=user_id,
                session_id=session_id,
                role=MessageRole.USER,
                message=user_message,
                intent=intent
            )
            self.db.add(user_conv)

            # Store assistant response
            assistant_conv = Conversation(
                user_id=user_id,
                session_id=session_id,
                role=MessageRole.ASSISTANT,
                message=assistant_response,
                intent=intent,
                agent_calls=[{"agent": agent_used}]  # Store which agent was used
            )
            self.db.add(assistant_conv)

            await self.db.commit()
            self.logger.info(f"Conversation stored for user {user_id}, session {session_id} (user + assistant)")
        except Exception as e:
            self.logger.error(f"Error storing conversation: {e}", exc_info=True)
            # Don't fail the request if conversation storage fails
            await self.db.rollback()

