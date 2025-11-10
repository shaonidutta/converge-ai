"""
Guardrail manager for orchestrating multiple guardrails.

This module provides the GuardrailManager class that coordinates the execution
of multiple guardrails in parallel and aggregates their results.
"""

import asyncio
from typing import List, Dict, Any, Optional
import logging

from .base_guardrail import BaseGuardrail
from .guardrail_result import GuardrailResult, GuardrailReport, Action

logger = logging.getLogger(__name__)


class GuardrailManager:
    """
    Manager for orchestrating multiple guardrails.
    
    This class coordinates the execution of multiple guardrails in parallel,
    aggregates their results, and determines the final action to take.
    """
    
    def __init__(self):
        """Initialize the GuardrailManager."""
        self.input_guardrails: List[BaseGuardrail] = []
        self.output_guardrails: List[BaseGuardrail] = []
        logger.info("GuardrailManager initialized")
    
    def register_input_guardrail(self, guardrail: BaseGuardrail):
        """
        Register an input guardrail.
        
        Args:
            guardrail: Input guardrail instance to register
        """
        if guardrail.is_enabled():
            self.input_guardrails.append(guardrail)
            logger.info(f"Registered input guardrail: {guardrail.name}")
        else:
            logger.info(f"Skipped disabled input guardrail: {guardrail.name}")
    
    def register_output_guardrail(self, guardrail: BaseGuardrail):
        """
        Register an output guardrail.
        
        Args:
            guardrail: Output guardrail instance to register
        """
        if guardrail.is_enabled():
            self.output_guardrails.append(guardrail)
            logger.info(f"Registered output guardrail: {guardrail.name}")
        else:
            logger.info(f"Skipped disabled output guardrail: {guardrail.name}")
    
    async def check_input(
        self,
        text: str,
        user_id: int,
        context: Optional[Dict[str, Any]] = None
    ) -> GuardrailReport:
        """
        Run all input guardrails in parallel.
        
        Args:
            text: User input text to check
            user_id: ID of the user sending the message
            context: Additional context (session_id, etc.)
        
        Returns:
            GuardrailReport with aggregated results
        """
        # Prepare context
        ctx = context or {}
        ctx['user_id'] = user_id
        ctx['check_type'] = 'input'
        
        logger.info(f"Running {len(self.input_guardrails)} input guardrails for user {user_id}")
        
        # Run all guardrails in parallel
        results = await self._run_guardrails_parallel(
            self.input_guardrails,
            text,
            ctx
        )
        
        # Create report
        report = GuardrailReport.from_results(results, text)
        
        logger.info(
            f"Input guardrails completed: action={report.final_action.value}, "
            f"blocked={report.is_blocked}, latency={report.total_latency_ms:.2f}ms"
        )
        
        return report
    
    async def check_output(
        self,
        text: str,
        user_id: int,
        context: Optional[Dict[str, Any]] = None
    ) -> GuardrailReport:
        """
        Run all output guardrails in parallel.
        
        Args:
            text: AI output text to check
            user_id: ID of the user receiving the message
            context: Additional context (session_id, etc.)
        
        Returns:
            GuardrailReport with aggregated results
        """
        # Prepare context
        ctx = context or {}
        ctx['user_id'] = user_id
        ctx['check_type'] = 'output'
        
        logger.info(f"Running {len(self.output_guardrails)} output guardrails for user {user_id}")
        
        # Run all guardrails in parallel
        results = await self._run_guardrails_parallel(
            self.output_guardrails,
            text,
            ctx
        )
        
        # Create report
        report = GuardrailReport.from_results(results, text)
        
        logger.info(
            f"Output guardrails completed: action={report.final_action.value}, "
            f"blocked={report.is_blocked}, latency={report.total_latency_ms:.2f}ms"
        )
        
        return report
    
    async def _run_guardrails_parallel(
        self,
        guardrails: List[BaseGuardrail],
        text: str,
        context: Dict[str, Any]
    ) -> List[GuardrailResult]:
        """
        Run multiple guardrails in parallel.
        
        Args:
            guardrails: List of guardrails to run
            text: Text to check
            context: Context dictionary
        
        Returns:
            List of GuardrailResult objects
        """
        if not guardrails:
            return []
        
        # Create tasks for all guardrails
        tasks = [
            guardrail.check_with_timeout(text, context)
            for guardrail in guardrails
        ]
        
        # Run all tasks in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # Guardrail raised an exception - create error result
                guardrail = guardrails[i]
                logger.error(
                    f"Guardrail {guardrail.name} raised exception: {str(result)}",
                    exc_info=result
                )
                
                error_result = GuardrailResult(
                    guardrail_name=guardrail.name,
                    action=Action.ALLOW,  # Fail-open on error
                    passed=True,
                    message=f"Guardrail error: {str(result)}",
                    details={"error": True, "error_message": str(result)}
                )
                processed_results.append(error_result)
            else:
                processed_results.append(result)
        
        return processed_results
    
    def get_input_guardrails_count(self) -> int:
        """
        Get the number of registered input guardrails.
        
        Returns:
            Number of input guardrails
        """
        return len(self.input_guardrails)
    
    def get_output_guardrails_count(self) -> int:
        """
        Get the number of registered output guardrails.
        
        Returns:
            Number of output guardrails
        """
        return len(self.output_guardrails)
    
    def get_guardrails_info(self) -> Dict[str, Any]:
        """
        Get information about registered guardrails.
        
        Returns:
            Dictionary with guardrails information
        """
        return {
            "input_guardrails": [
                {
                    "name": g.name,
                    "enabled": g.is_enabled(),
                    "timeout": g.timeout
                }
                for g in self.input_guardrails
            ],
            "output_guardrails": [
                {
                    "name": g.name,
                    "enabled": g.is_enabled(),
                    "timeout": g.timeout
                }
                for g in self.output_guardrails
            ],
            "total_input": len(self.input_guardrails),
            "total_output": len(self.output_guardrails)
        }

