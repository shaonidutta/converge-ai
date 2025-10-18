"""
Agent Execution Graph (Graph 2)

Handles parallel and sequential execution of multiple agents with:
- Dependency resolution
- Timeout handling
- Error recovery
- Response merging with provenance tracking

Flow:
1. Prepare execution → Analyze intents and determine dependencies
2. Execute parallel agents → Run independent agents concurrently
3. Execute sequential agents → Run dependent agents sequentially
4. Merge responses → Combine all responses with provenance

Design Principles:
- Thin nodes (just call services)
- Async operations with asyncio.gather() for parallelism
- Stateless (context-aware via state parameter)
- Comprehensive error handling
- Performance optimized
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from langgraph.graph import StateGraph, END

from src.graphs.state import AgentExecutionState

logger = logging.getLogger(__name__)


# ============================================================
# DEPENDENCY RESOLUTION
# ============================================================

# Define agent dependencies
# Format: {intent_type: [required_intents]}
INTENT_DEPENDENCIES = {
    "booking_modify": ["booking_create", "booking_status"],
    "booking_reschedule": ["booking_create", "booking_status"],
    "complaint": ["booking_status"],
    "booking_cancel": ["booking_status"],  # May need booking info first
}


def has_dependencies(intent: Dict[str, Any], all_intents: List[Dict[str, Any]]) -> bool:
    """
    Check if an intent depends on another intent
    
    Args:
        intent: Intent to check
        all_intents: All intents in the request
        
    Returns:
        True if intent has dependencies, False otherwise
    """
    intent_type = intent.get("intent", "")
    
    if intent_type not in INTENT_DEPENDENCIES:
        return False
    
    # Check if any dependency exists in all_intents
    required_intents = INTENT_DEPENDENCIES[intent_type]
    for other_intent in all_intents:
        if other_intent.get("intent") in required_intents:
            return True
    
    return False


# ============================================================
# NODE FUNCTIONS (Thin, Async, Stateless)
# ============================================================

async def prepare_agent_execution_node(
    state: AgentExecutionState,
) -> Dict[str, Any]:
    """
    Node: Prepare for agent execution
    
    Analyzes intents and determines execution plan:
    - Independent intents → Parallel execution
    - Dependent intents → Sequential execution
    
    Args:
        state: Current conversation state
        
    Returns:
        Updated state with execution plan
    """
    try:
        logger.info("[prepare_agent_execution_node] Analyzing intents for execution plan")
        
        intent_result = state.get("intent_result", {})
        intents = intent_result.get("intents", [])
        
        if not intents:
            logger.warning("[prepare_agent_execution_node] No intents found")
            return {
                "independent_intents": [],
                "dependent_intents": [],
                "execution_plan": {"parallel_batch": [], "sequential_batch": []},
                "metadata": {
                    **state.get("metadata", {}),
                    "nodes_executed": state.get("metadata", {}).get("nodes_executed", []) + ["prepare_agent_execution_node"]
                }
            }
        
        # Separate independent and dependent intents
        independent_intents = []
        dependent_intents = []
        
        for intent in intents:
            if has_dependencies(intent, intents):
                dependent_intents.append(intent)
            else:
                independent_intents.append(intent)
        
        execution_plan = {
            "parallel_batch": independent_intents,
            "sequential_batch": dependent_intents,
            "total_intents": len(intents),
            "parallel_count": len(independent_intents),
            "sequential_count": len(dependent_intents)
        }
        
        logger.info(
            f"[prepare_agent_execution_node] Execution plan: "
            f"{len(independent_intents)} parallel, {len(dependent_intents)} sequential"
        )
        
        return {
            "independent_intents": independent_intents,
            "dependent_intents": dependent_intents,
            "execution_plan": execution_plan,
            "metadata": {
                **state.get("metadata", {}),
                "nodes_executed": state.get("metadata", {}).get("nodes_executed", []) + ["prepare_agent_execution_node"],
                "execution_plan": execution_plan
            }
        }
    
    except Exception as e:
        logger.error(f"[prepare_agent_execution_node] Error: {e}", exc_info=True)
        return {
            "error": {
                "message": str(e),
                "node": "prepare_agent_execution_node",
                "type": "PreparationError"
            }
        }


async def execute_parallel_agents_node(
    state: AgentExecutionState,
    coordinator_agent: Any  # CoordinatorAgent instance
) -> Dict[str, Any]:
    """
    Node: Execute independent agents in parallel
    
    Uses asyncio.gather() for concurrent execution with:
    - Timeout handling
    - Error recovery
    - Performance tracking
    
    Args:
        state: Current conversation state
        coordinator_agent: CoordinatorAgent instance
        
    Returns:
        Updated state with parallel responses
    """
    try:
        independent_intents = state.get("independent_intents", [])
        
        if not independent_intents:
            logger.info("[execute_parallel_agents_node] No independent intents to execute")
            return {
                "parallel_responses": [],
                "metadata": {
                    **state.get("metadata", {}),
                    "nodes_executed": state.get("metadata", {}).get("nodes_executed", []) + ["execute_parallel_agents_node"]
                }
            }
        
        logger.info(f"[execute_parallel_agents_node] Executing {len(independent_intents)} agents in parallel")

        start_time = datetime.now(timezone.utc)
        
        # Create tasks for parallel execution
        tasks = []
        for intent in independent_intents:
            task = coordinator_agent._route_to_agent_with_timing(
                intent_result=intent,
                user=state.get("user"),
                session_id=state.get("session_id", "")
            )
            tasks.append(task)
        
        # Execute in parallel with timeout
        timeout = state.get("agent_timeout", 30)
        
        try:
            responses = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            logger.error(f"[execute_parallel_agents_node] Timeout after {timeout}s")
            responses = [
                {
                    "response": f"Agent execution timed out for {intent.get('intent')}",
                    "action_taken": "timeout",
                    "agent_used": "timeout",
                    "error": "TimeoutError"
                }
                for intent in independent_intents
            ]
        
        # Process responses and handle exceptions
        parallel_responses = []
        agents_used = []
        
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                logger.error(f"[execute_parallel_agents_node] Agent {i} failed: {response}")
                parallel_responses.append({
                    "response": f"Error processing {independent_intents[i].get('intent')}",
                    "action_taken": "error",
                    "agent_used": "error",
                    "error": str(response)
                })
            else:
                parallel_responses.append(response)
                agents_used.append(response.get("agent_used", "unknown"))

        end_time = datetime.now(timezone.utc)
        execution_time_ms = int((end_time - start_time).total_seconds() * 1000)
        
        logger.info(
            f"[execute_parallel_agents_node] Completed {len(parallel_responses)} agents "
            f"in {execution_time_ms}ms"
        )
        
        return {
            "parallel_responses": parallel_responses,
            "agents_used": state.get("agents_used", []) + agents_used,
            "metadata": {
                **state.get("metadata", {}),
                "nodes_executed": state.get("metadata", {}).get("nodes_executed", []) + ["execute_parallel_agents_node"],
                "parallel_execution_time_ms": execution_time_ms,
                "parallel_agents_count": len(parallel_responses)
            }
        }
    
    except Exception as e:
        logger.error(f"[execute_parallel_agents_node] Error: {e}", exc_info=True)
        return {
            "error": {
                "message": str(e),
                "node": "execute_parallel_agents_node",
                "type": "ParallelExecutionError"
            }
        }


async def execute_sequential_agents_node(
    state: AgentExecutionState,
    coordinator_agent: Any  # CoordinatorAgent instance
) -> Dict[str, Any]:
    """
    Node: Execute dependent agents sequentially
    
    Each agent can use results from previous agents.
    
    Args:
        state: Current conversation state
        coordinator_agent: CoordinatorAgent instance
        
    Returns:
        Updated state with sequential responses
    """
    try:
        dependent_intents = state.get("dependent_intents", [])
        
        if not dependent_intents:
            logger.info("[execute_sequential_agents_node] No dependent intents to execute")
            return {
                "sequential_responses": [],
                "metadata": {
                    **state.get("metadata", {}),
                    "nodes_executed": state.get("metadata", {}).get("nodes_executed", []) + ["execute_sequential_agents_node"]
                }
            }
        
        logger.info(f"[execute_sequential_agents_node] Executing {len(dependent_intents)} agents sequentially")

        start_time = datetime.now(timezone.utc)
        
        parallel_responses = state.get("parallel_responses", [])
        sequential_responses = []
        agents_used = []
        
        for intent in dependent_intents:
            # Add context from previous responses
            intent_with_context = {
                **intent,
                "context": {
                    "parallel_results": parallel_responses,
                    "sequential_results": sequential_responses
                }
            }
            
            try:
                response = await coordinator_agent._route_to_agent_with_timing(
                    intent_result=intent_with_context,
                    user=state.get("user"),
                    session_id=state.get("session_id", "")
                )
                sequential_responses.append(response)
                agents_used.append(response.get("agent_used", "unknown"))
            except Exception as e:
                logger.error(f"[execute_sequential_agents_node] Agent failed: {e}")
                sequential_responses.append({
                    "response": f"Error processing {intent.get('intent')}",
                    "action_taken": "error",
                    "agent_used": "error",
                    "error": str(e)
                })

        end_time = datetime.now(timezone.utc)
        execution_time_ms = int((end_time - start_time).total_seconds() * 1000)
        
        logger.info(
            f"[execute_sequential_agents_node] Completed {len(sequential_responses)} agents "
            f"in {execution_time_ms}ms"
        )
        
        return {
            "sequential_responses": sequential_responses,
            "agents_used": state.get("agents_used", []) + agents_used,
            "metadata": {
                **state.get("metadata", {}),
                "nodes_executed": state.get("metadata", {}).get("nodes_executed", []) + ["execute_sequential_agents_node"],
                "sequential_execution_time_ms": execution_time_ms,
                "sequential_agents_count": len(sequential_responses)
            }
        }
    
    except Exception as e:
        logger.error(f"[execute_sequential_agents_node] Error: {e}", exc_info=True)
        return {
            "error": {
                "message": str(e),
                "node": "execute_sequential_agents_node",
                "type": "SequentialExecutionError"
            }
        }


async def merge_responses_node(
    state: AgentExecutionState
) -> Dict[str, Any]:
    """
    Node: Merge responses from all agents with provenance tracking

    Creates a user-friendly combined response with:
    - Clear attribution (which agent said what)
    - Proper formatting
    - Provenance tracking for transparency
    - Combined metadata

    Args:
        state: Current conversation state

    Returns:
        Updated state with final response and provenance
    """
    try:
        logger.info("[merge_responses_node] Merging responses from all agents")

        parallel_responses = state.get("parallel_responses", [])
        sequential_responses = state.get("sequential_responses", [])

        all_responses = parallel_responses + sequential_responses

        if not all_responses:
            logger.warning("[merge_responses_node] No responses to merge")
            return {
                "final_response": "I couldn't process your request. Please try again.",
                "response_type": "error",
                "metadata": {
                    **state.get("metadata", {}),
                    "nodes_executed": state.get("metadata", {}).get("nodes_executed", []) + ["merge_responses_node"]
                }
            }

        # Build provenance and response parts
        provenance = []
        response_parts = []
        combined_metadata = {}
        successful_agents = 0
        failed_agents = 0

        for i, resp in enumerate(all_responses):
            agent_used = resp.get("agent_used", "unknown")
            response_text = resp.get("response", "")
            action_taken = resp.get("action_taken", "unknown")
            metadata = resp.get("metadata", {})
            error = resp.get("error")
            execution_time_ms = resp.get("execution_time_ms", 0)

            # Track success/failure
            if error or action_taken in ["error", "timeout"]:
                failed_agents += 1
            else:
                successful_agents += 1

            # Add to provenance
            provenance_entry = {
                "agent": agent_used,
                "contribution": response_text,
                "action_taken": action_taken,
                "order": i + 1,
                "execution_time_ms": execution_time_ms,
                "success": not error
            }

            if error:
                provenance_entry["error"] = error

            provenance.append(provenance_entry)

            # Add to response parts (only successful responses)
            if response_text and not error:
                response_parts.append(response_text)

            # Merge metadata
            if metadata:
                combined_metadata[agent_used] = metadata

        # Format final response
        if len(response_parts) == 0:
            final_response = "I encountered errors processing your request. Please try again."
        elif len(response_parts) == 1:
            # Single response - no need for formatting
            final_response = response_parts[0]
        else:
            # Multiple responses - format with clear sections
            formatted_parts = []
            for prov, part in zip(provenance, response_parts):
                agent_name = prov["agent"].replace("_", " ").title()
                formatted_parts.append(f"**{agent_name}**: {part}")

            final_response = "\n\n".join(formatted_parts)

        end_time = datetime.now(timezone.utc)

        logger.info(
            f"[merge_responses_node] Merged {len(all_responses)} responses "
            f"({successful_agents} successful, {failed_agents} failed)"
        )

        return {
            "final_response": final_response,
            "response_type": "answer",
            "provenance": provenance,
            "combined_metadata": combined_metadata,
            "graph_end_time": end_time.isoformat(),
            "metadata": {
                **state.get("metadata", {}),
                "nodes_executed": state.get("metadata", {}).get("nodes_executed", []) + ["merge_responses_node"],
                "total_responses": len(all_responses),
                "successful_agents": successful_agents,
                "failed_agents": failed_agents
            }
        }

    except Exception as e:
        logger.error(f"[merge_responses_node] Error: {e}", exc_info=True)
        return {
            "error": {
                "message": str(e),
                "node": "merge_responses_node",
                "type": "ResponseMergingError"
            }
        }


# ============================================================
# GRAPH CREATION
# ============================================================

def create_agent_execution_graph(coordinator_agent: Any) -> StateGraph:
    """
    Create the Agent Execution Graph

    Flow:
    1. prepare_agent_execution → Analyze intents and plan execution
    2. execute_parallel_agents → Run independent agents concurrently
    3. execute_sequential_agents → Run dependent agents sequentially
    4. merge_responses → Combine all responses with provenance

    Args:
        coordinator_agent: CoordinatorAgent instance

    Returns:
        Compiled StateGraph
    """
    logger.info("[create_agent_execution_graph] Creating agent execution graph")

    # Create graph
    graph = StateGraph(AgentExecutionState)

    # Add nodes with dependency injection
    async def _prepare(state):
        return await prepare_agent_execution_node(state)

    async def _parallel(state):
        return await execute_parallel_agents_node(state, coordinator_agent)

    async def _sequential(state):
        return await execute_sequential_agents_node(state, coordinator_agent)

    async def _merge(state):
        return await merge_responses_node(state)

    graph.add_node("prepare_agent_execution", _prepare)
    graph.add_node("execute_parallel_agents", _parallel)
    graph.add_node("execute_sequential_agents", _sequential)
    graph.add_node("merge_responses", _merge)

    # Set entry point
    graph.set_entry_point("prepare_agent_execution")

    # Add edges (linear flow)
    graph.add_edge("prepare_agent_execution", "execute_parallel_agents")
    graph.add_edge("execute_parallel_agents", "execute_sequential_agents")
    graph.add_edge("execute_sequential_agents", "merge_responses")
    graph.add_edge("merge_responses", END)

    logger.info("[create_agent_execution_graph] Graph created successfully")

    # Compile and return
    return graph.compile()

