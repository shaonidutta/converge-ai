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
        "booking_reschedule": "booking",
        "booking_cancel": "cancellation",  # Route to dedicated CancellationAgent
        "booking_status": "booking",
        "complaint": "complaint",  # Route to ComplaintAgent
        "data_query": "sql",  # Route to SQLAgent for data queries
        "general_query": "coordinator",  # Handle general queries in coordinator
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
            
            # Initialize specialized agents
            self.policy_agent = PolicyAgent(db=db)
            self.service_agent = ServiceAgent(db=db)
            self.booking_agent = BookingAgent(db=db)
            self.cancellation_agent = CancellationAgent(db=db)
            self.complaint_agent = ComplaintAgent(db=db)
            self.sql_agent = SQLAgent(db=db)
            
            self.logger.info("CoordinatorAgent initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing CoordinatorAgent: {e}")
            raise
    
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

            # Check if there's an active dialog state (ongoing slot-filling)
            from src.services.dialog_state_manager import DialogStateManager
            dialog_manager = DialogStateManager(self.db)
            dialog_state = await dialog_manager.get_active_state(session_id)

            # If there's an active dialog state, use slot-filling service
            if dialog_state:
                self.logger.info(f"Active dialog state found: {dialog_state.intent}, state: {dialog_state.state}")
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

                # If slot-filling is complete, execute the agent
                if result.should_trigger_agent:
                    self.logger.info(f"Slot-filling complete, executing agent with entities: {result.collected_entities}")

                    # Map entity names to match agent expectations
                    # LLM may extract 'zip_code' but agents expect 'location'
                    mapped_entities = result.collected_entities.copy()
                    if 'zip_code' in mapped_entities and 'location' not in mapped_entities:
                        mapped_entities['location'] = mapped_entities.pop('zip_code')
                        self.logger.info(f"Mapped 'zip_code' to 'location': {mapped_entities.get('location')}")

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
                        message=message
                    )

                    # Clear the dialog state
                    await dialog_manager.clear_state(session_id)

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

                    # Determine actual required entities based on action
                    # Order matters: location first (to check availability), then date/time
                    if action == "book":
                        required_entities = ["service_type", "location", "date", "time"]
                    elif action == "cancel":
                        required_entities = ["booking_id"]
                    elif action == "reschedule":
                        required_entities = ["booking_id", "date", "time"]
                    elif action == "modify":
                        required_entities = ["booking_id"]

                    self.logger.info(f"booking_management action={action}, required_entities={required_entities}")

                missing_entities = [e for e in required_entities if e not in collected_entities]

                if missing_entities:
                    self.logger.info(f"Missing entities: {missing_entities}, starting slot-filling")

                    # Create dialog state for this session
                    from src.schemas.dialog_state import DialogStateCreate
                    from src.core.models.dialog_state import DialogStateType

                    dialog_state_data = DialogStateCreate(
                        session_id=session_id,
                        user_id=user_id,
                        intent=intent_result.primary_intent,
                        state=DialogStateType.COLLECTING_INFO,
                        collected_entities=collected_entities,
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
                    message=message  # Pass original message for agents that need it
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
        message: str = ""  # Original message for agents that need it
    ) -> Dict[str, Any]:
        """
        Route request to appropriate specialized agent

        Args:
            intent_result: Classified intent with entities
            user: User object
            session_id: Session ID
            message: Original user message (for agents that need full context)

        Returns:
            Agent response dictionary
        """
        intent = intent_result.intent
        entities = intent_result.entities

        # Determine which agent to use
        agent_type = self.INTENT_AGENT_MAP.get(intent, "policy")

        self.logger.info(f"Routing intent '{intent}' to {agent_type} agent")

        try:
            # Handle coordinator-level intents (greetings, general queries)
            if agent_type == "coordinator":
                if intent == "greeting":
                    return await self._handle_greeting(user, message)
                elif intent == "general_query":
                    return await self._handle_general_query(user, message)
                else:
                    # Unknown coordinator intent, fallback to policy
                    self.logger.warning(f"Unknown coordinator intent '{intent}', falling back to policy agent")
                    agent_type = "policy"

            if agent_type == "policy":
                response = await self.policy_agent.execute(
                    intent=intent,
                    entities=entities,
                    user=user,
                    session_id=session_id
                )
                response["agent_used"] = "policy"
                
            elif agent_type == "service":
                response = await self.service_agent.execute(
                    intent=intent,
                    entities=entities,
                    user=user,
                    session_id=session_id
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
                    message="",  # Message not needed for cancellation
                    user=user,
                    session_id=session_id,
                    entities=entities
                )
                response["agent_used"] = "cancellation"

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
                    session_id=session_id
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

    async def _handle_greeting(self, user: User, message: str) -> Dict[str, Any]:
        """
        Handle greeting intent

        Greetings are simple, stateless responses that don't require specialized agent logic.

        Args:
            user: User object
            message: Original greeting message

        Returns:
            Greeting response dictionary
        """
        user_name = user.first_name or "there"

        # Generate natural greeting response
        response = (
            f"Hi {user_name}! I'm Lisa, your ConvergeAI assistant. "
            f"I can help you book home services like AC repair, plumbing, cleaning, and more. "
            f"I can also check prices, manage your bookings, and answer policy questions. "
            f"What can I do for you today?"
        )

        self.logger.info(f"Handled greeting for user {user.id}")

        return {
            "response": response,
            "action_taken": "greeting_handled",
            "agent_used": "coordinator",
            "metadata": {
                "user_name": user_name,
                "greeting_message": message
            }
        }

    async def _handle_general_query(self, user: User, message: str) -> Dict[str, Any]:
        """
        Handle general query intent

        General queries are broad questions that don't fit specific categories.
        Provide helpful information about available services.

        Args:
            user: User object
            message: Original query message

        Returns:
            General query response dictionary
        """
        # For general queries, provide helpful information
        response = (
            f"I'm here to help! I can assist you with booking home services, "
            f"checking prices and availability, managing your bookings, "
            f"handling complaints, and answering policy questions. "
            f"What would you like to know?"
        )

        self.logger.info(f"Handled general query for user {user.id}: {message[:50]}...")

        return {
            "response": response,
            "action_taken": "general_query_handled",
            "agent_used": "coordinator",
            "metadata": {
                "query": message
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
                session_id=session_id
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
                    message=message  # Pass original message
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

