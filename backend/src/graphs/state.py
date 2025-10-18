"""
LangGraph State Definitions

Defines the state structure for all conversation graphs.
"""

from typing import TypedDict, Optional, List, Dict, Any
from datetime import datetime


class ConversationState(TypedDict, total=False):
    """
    Shared state for all conversation graphs
    
    This state is passed between nodes and graphs.
    Each node can read from and write to this state.
    
    Design Principles:
    - Immutable updates (nodes return new state, don't modify in place)
    - Context-aware (contains all info needed for stateless nodes)
    - Serializable (can be stored/retrieved from DB)
    """
    
    # ============================================================
    # USER CONTEXT
    # ============================================================
    user_id: int
    """User ID from authentication"""
    
    session_id: str
    """Conversation session ID"""
    
    channel: str
    """Communication channel (web, mobile, whatsapp)"""
    
    # ============================================================
    # CURRENT MESSAGE
    # ============================================================
    current_message: str
    """Current user message being processed"""
    
    message_timestamp: str
    """ISO timestamp of current message"""
    
    conversation_history: List[Dict[str, str]]
    """
    Previous messages in conversation
    Format: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
    Limited to last 10 messages for context
    """
    
    # ============================================================
    # INTENT CLASSIFICATION
    # ============================================================
    intent_result: Optional[Dict[str, Any]]
    """
    Result from IntentClassifier.classify()
    Contains: primary_intent, confidence, entities, etc.
    """
    
    primary_intent: Optional[str]
    """Primary intent detected (e.g., 'booking_management')"""
    
    intent_confidence: Optional[float]
    """Confidence score for primary intent (0.0 to 1.0)"""
    
    classification_method: Optional[str]
    """Method used: 'pattern_match', 'llm', 'context_aware_llm', 'fallback'"""
    
    # ============================================================
    # DIALOG STATE (Slot-Filling)
    # ============================================================
    dialog_state_id: Optional[int]
    """Database ID of active dialog state"""
    
    dialog_state_type: Optional[str]
    """Current state: 'idle', 'collecting_info', 'awaiting_confirmation', etc."""
    
    collected_entities: Dict[str, Any]
    """
    Entities collected so far
    Example: {"service_type": "ac", "date": "2025-10-10", "time": "14:00"}
    """
    
    needed_entities: List[str]
    """
    Entities still needed
    Example: ["location", "time"]
    """
    
    is_follow_up: Optional[bool]
    """Whether current message is a follow-up response"""
    
    follow_up_confidence: Optional[float]
    """Confidence that this is a follow-up (0.0 to 1.0)"""
    
    expected_entity: Optional[str]
    """Entity type expected in follow-up response"""
    
    # ============================================================
    # ENTITY EXTRACTION & VALIDATION
    # ============================================================
    extracted_entity: Optional[Dict[str, Any]]
    """
    Entity extracted from current message
    Format: {"entity_type": "date", "entity_value": "tomorrow", "normalized_value": "2025-10-10"}
    """
    
    validation_result: Optional[Dict[str, Any]]
    """
    Result from entity validation
    Format: {"is_valid": True, "normalized_value": "...", "error_message": None}
    """
    
    validation_errors: List[str]
    """List of validation error messages"""
    
    # ============================================================
    # QUESTION GENERATION
    # ============================================================
    current_question: Optional[str]
    """Question to ask user for missing entity"""
    
    last_question_asked: Optional[str]
    """Last question asked (for context)"""
    
    question_attempt_count: int
    """Number of times we've asked for the same entity (for retry logic)"""
    
    # ============================================================
    # CONFIRMATION
    # ============================================================
    confirmation_message: Optional[str]
    """Confirmation message with all collected entities"""
    
    user_confirmed: Optional[bool]
    """Whether user confirmed the collected information"""
    
    # ============================================================
    # AGENT EXECUTION (Single Agent)
    # ============================================================
    agent_name: Optional[str]
    """Name of agent to execute (e.g., 'BookingAgent', 'SQLAgent')"""

    agent_input: Optional[Dict[str, Any]]
    """Input data for agent execution"""

    agent_result: Optional[Dict[str, Any]]
    """Result from agent execution"""

    agent_error: Optional[str]
    """Error message if agent execution failed"""

    # ============================================================
    # MULTI-AGENT EXECUTION
    # ============================================================
    independent_intents: List[Dict[str, Any]]
    """Intents that can be executed in parallel (no dependencies)"""

    dependent_intents: List[Dict[str, Any]]
    """Intents that must be executed sequentially (have dependencies)"""

    execution_plan: Optional[Dict[str, Any]]
    """
    Execution plan for multi-agent orchestration
    Format: {"parallel_batch": [...], "sequential_batch": [...]}
    """

    parallel_responses: List[Dict[str, Any]]
    """Responses from parallel agent execution"""

    sequential_responses: List[Dict[str, Any]]
    """Responses from sequential agent execution"""

    agent_timeout: int
    """Timeout in seconds for agent execution (default: 30)"""

    agents_used: List[str]
    """List of agent names that were executed"""
    
    # ============================================================
    # RESPONSE GENERATION
    # ============================================================
    final_response: str
    """Final response to send to user"""
    
    response_type: Optional[str]
    """Type of response: 'question', 'confirmation', 'answer', 'error'"""
    
    # ============================================================
    # METADATA & TRACKING
    # ============================================================
    metadata: Dict[str, Any]
    """
    Additional metadata for tracking
    Example: {"graph_name": "slot_filling", "nodes_executed": [...], "execution_time_ms": 150}
    """
    
    provenance: Optional[List[Dict[str, Any]]]
    """
    Source tracking for response with detailed agent contributions
    Format: [
        {
            "agent": "service",
            "contribution": "AC service costs ₹500...",
            "action_taken": "service_info_retrieved",
            "order": 1,
            "execution_time_ms": 150
        },
        {
            "agent": "policy",
            "contribution": "Cancellation policy allows...",
            "action_taken": "policy_retrieved",
            "order": 2,
            "execution_time_ms": 200
        }
    ]
    """

    combined_metadata: Optional[Dict[str, Any]]
    """
    Combined metadata from all agent executions
    Format: {"service": {...}, "policy": {...}}
    """
    
    # ============================================================
    # ERROR HANDLING
    # ============================================================
    error: Optional[Dict[str, Any]]
    """
    Error information if something went wrong
    Format: {"type": "ValidationError", "message": "...", "node": "validate_entity_node"}
    """
    
    retry_count: int
    """Number of retries for current operation"""
    
    max_retries: int
    """Maximum number of retries allowed (default: 3)"""
    
    # ============================================================
    # GRAPH CONTROL
    # ============================================================
    next_graph: Optional[str]
    """Name of next graph to execute (for graph chaining)"""
    
    should_end: bool
    """Whether to end the conversation flow"""
    
    # ============================================================
    # TIMESTAMPS
    # ============================================================
    graph_start_time: Optional[str]
    """ISO timestamp when graph execution started"""
    
    graph_end_time: Optional[str]
    """ISO timestamp when graph execution ended"""


class SlotFillingState(ConversationState):
    """
    State specific to Slot-Filling Graph
    Inherits all fields from ConversationState
    """
    pass


class AgentExecutionState(ConversationState):
    """
    State specific to Agent Execution Graph
    Inherits all fields from ConversationState
    """
    pass


class ErrorHandlingState(ConversationState):
    """
    State specific to Error Handling Graph
    Inherits all fields from ConversationState
    """
    pass


# ============================================================
# STATE INITIALIZATION HELPERS
# ============================================================

def create_initial_state(
    user_id: int,
    session_id: str,
    current_message: str,
    channel: str = "web",
    conversation_history: Optional[List[Dict[str, str]]] = None
) -> ConversationState:
    """
    Create initial state for conversation processing
    
    Args:
        user_id: User ID
        session_id: Session ID
        current_message: Current user message
        channel: Communication channel
        conversation_history: Previous messages
        
    Returns:
        Initial ConversationState
    """
    return ConversationState(
        # User context
        user_id=user_id,
        session_id=session_id,
        channel=channel,
        
        # Current message
        current_message=current_message,
        message_timestamp=datetime.utcnow().isoformat(),
        conversation_history=conversation_history or [],
        
        # Initialize empty/default values
        collected_entities={},
        needed_entities=[],
        validation_errors=[],
        metadata={},

        # Multi-agent execution
        independent_intents=[],
        dependent_intents=[],
        parallel_responses=[],
        sequential_responses=[],
        agent_timeout=30,
        agents_used=[],
        
        # Counters
        question_attempt_count=0,
        retry_count=0,
        max_retries=3,
        
        # Control flags
        should_end=False,
        
        # Response
        final_response="",
        
        # Timestamps
        graph_start_time=datetime.utcnow().isoformat()
    )

