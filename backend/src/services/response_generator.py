"""
ResponseGenerator Service - LLM-based Natural Response Generation

This service generates natural, conversational responses using LLM instead of
hardcoded templates. It makes Lisa feel more human and less robotic.

Key Features:
- Context-aware responses using conversation history
- Personalized responses using user's name
- Warm, empathetic, conversational tone
- No emojis or structured formatting
- Fallback to templates if LLM fails
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from src.llm.gemini.client import LLMClient

logger = logging.getLogger(__name__)


# Lisa's personality prompt
LISA_PERSONALITY = """You are Lisa, a friendly and helpful AI assistant for ConvergeAI home services.

Your personality:
- Warm, empathetic, and personable
- Speak naturally, like a human friend would
- Be conversational, not transactional
- Show genuine care for the user's needs
- Use simple, clear language

Guidelines:
- NEVER use emojis (❌ ✅ 🔹 📋 ⏰ 📞 etc.)
- NEVER use bullet points or numbered lists
- NEVER use structured formatting
- Avoid robotic phrases like "I'd be happy to help" or "Could you please clarify"
- Reference previous conversation naturally when relevant
- Personalize responses using user's name when appropriate
- Be concise but warm (2-4 sentences usually)
- Sound like you're having a conversation, not filling out a form

Remember: You're chatting with a friend, not writing a business email!"""


class ResponseGenerator:
    """
    Generates natural, conversational responses using LLM
    """
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        """
        Initialize ResponseGenerator
        
        Args:
            llm_client: LLM client for generation (if None, will create one)
        """
        self.llm_client = llm_client or LLMClient()
        self.logger = logging.getLogger(__name__)
    
    async def generate_booking_confirmation(
        self,
        booking_data: Dict[str, Any],
        conversation_history: Optional[List[Dict[str, str]]] = None,
        user_name: Optional[str] = None
    ) -> str:
        """
        Generate natural booking confirmation response

        Args:
            booking_data: Booking details (order_id, total_amount, date, time)
            conversation_history: Previous conversation messages
            user_name: User's first name for personalization

        Returns:
            Natural, conversational confirmation message
        """
        try:
            # Build context
            context = self._build_context(conversation_history, user_name)

            # Build prompt
            prompt = f"""{LISA_PERSONALITY}

{context}

TASK: Generate a natural, conversational booking confirmation message.

BOOKING DETAILS:
- Order ID: {booking_data.get('order_id')}
- Total Amount: ₹{booking_data.get('total_amount')}
- Date: {booking_data.get('date')}
- Time: {booking_data.get('time')}

INSTRUCTIONS:
1. Confirm the booking naturally (don't just list details)
2. Mention the order ID, amount, date, and time conversationally
3. Sound excited and helpful
4. Keep it to 2-3 sentences
5. NO emojis, NO bullet points, NO structured formatting

Generate the response:"""

            # Call LLM
            response = self.llm_client.generate(prompt)
            response_text = response.strip()

            self.logger.info(f"[ResponseGenerator] Generated booking confirmation: {response_text[:100]}...")
            return response_text

        except Exception as e:
            self.logger.error(f"[ResponseGenerator] Error generating booking confirmation: {e}")
            # Fallback to simple template
            return (
                f"Great! Your booking is confirmed. "
                f"Order ID {booking_data.get('order_id')}, "
                f"total amount ₹{booking_data.get('total_amount')}, "
                f"scheduled for {booking_data.get('date')} at {booking_data.get('time')}."
            )
    
    async def generate_cancellation_response(
        self,
        cancellation_data: Dict[str, Any],
        conversation_history: Optional[List[Dict[str, str]]] = None,
        user_name: Optional[str] = None
    ) -> str:
        """
        Generate natural cancellation response
        
        Args:
            cancellation_data: Cancellation details (booking_number, refund_amount)
            conversation_history: Previous conversation messages
            user_name: User's first name for personalization
            
        Returns:
            Natural, conversational cancellation message
        """
        try:
            context = self._build_context(conversation_history, user_name)
            
            prompt = f"""{LISA_PERSONALITY}

{context}

TASK: Generate a natural, empathetic cancellation confirmation message.

CANCELLATION DETAILS:
- Booking Number: {cancellation_data.get('booking_number')}
- Refund Amount: ₹{cancellation_data.get('refund_amount')}

INSTRUCTIONS:
1. Acknowledge the cancellation with empathy
2. Mention the refund amount and timeline (5-7 business days)
3. Sound understanding and helpful
4. Keep it to 2-3 sentences
5. NO emojis, NO bullet points, NO structured formatting

Generate the response:"""

            response = self.llm_client.generate(prompt)
            response_text = response.strip()
            
            self.logger.info(f"[ResponseGenerator] Generated cancellation response: {response_text[:100]}...")
            return response_text
            
        except Exception as e:
            self.logger.error(f"[ResponseGenerator] Error generating cancellation response: {e}")
            return (
                f"I've cancelled booking {cancellation_data.get('booking_number')}. "
                f"Your refund of ₹{cancellation_data.get('refund_amount')} will be processed within 5-7 business days."
            )
    
    async def generate_service_list_response(
        self,
        services: List[Dict[str, Any]],
        conversation_history: Optional[List[Dict[str, str]]] = None,
        user_name: Optional[str] = None
    ) -> str:
        """
        Generate natural service listing response
        
        Args:
            services: List of services with name and price
            conversation_history: Previous conversation messages
            user_name: User's first name for personalization
            
        Returns:
            Natural, conversational service listing message
        """
        try:
            context = self._build_context(conversation_history, user_name)
            
            # Format services for prompt
            services_text = "\n".join([
                f"- {s['name']}: ₹{s['price']}" + (f" (was ₹{s['strike_price']})" if s.get('strike_price') else "")
                for s in services
            ])
            
            prompt = f"""{LISA_PERSONALITY}

{context}

TASK: Generate a natural, conversational message listing available services.

SERVICES:
{services_text}

INSTRUCTIONS:
1. Present the services naturally (not as a numbered list)
2. Mention prices conversationally
3. Ask if they'd like more details or want to book
4. Keep it friendly and helpful
5. NO emojis, NO bullet points in the response, NO structured formatting

Generate the response:"""

            response = self.llm_client.generate(prompt)
            response_text = response.strip()
            
            self.logger.info(f"[ResponseGenerator] Generated service list response: {response_text[:100]}...")
            return response_text
            
        except Exception as e:
            self.logger.error(f"[ResponseGenerator] Error generating service list response: {e}")
            services_str = ", ".join([f"{s['name']} (₹{s['price']})" for s in services[:3]])
            return f"Here are the available services: {services_str}. Would you like details on any of these, or shall I help you book one?"
    
    async def generate_complaint_response(
        self,
        complaint_data: Dict[str, Any],
        conversation_history: Optional[List[Dict[str, str]]] = None,
        user_name: Optional[str] = None
    ) -> str:
        """
        Generate natural complaint registration response
        
        Args:
            complaint_data: Complaint details (complaint_id, type, priority, sla_hours)
            conversation_history: Previous conversation messages
            user_name: User's first name for personalization
            
        Returns:
            Natural, empathetic complaint response
        """
        try:
            context = self._build_context(conversation_history, user_name)
            
            prompt = f"""{LISA_PERSONALITY}

{context}

TASK: Generate a natural, empathetic complaint registration message.

COMPLAINT DETAILS:
- Complaint ID: #{complaint_data.get('complaint_id')}
- Type: {complaint_data.get('type')}
- Priority: {complaint_data.get('priority')}
- Expected Response: Within {complaint_data.get('sla_response_hours')} hour(s)
- Expected Resolution: Within {complaint_data.get('sla_resolution_hours')} hour(s)

INSTRUCTIONS:
1. Show empathy and understanding
2. Confirm the complaint is registered
3. Mention the complaint ID and expected response time naturally
4. Reassure them that support will contact them
5. Keep it warm and caring (2-3 sentences)
6. NO emojis, NO bullet points, NO structured formatting

Generate the response:"""

            response = self.llm_client.generate(prompt)
            response_text = response.strip()
            
            self.logger.info(f"[ResponseGenerator] Generated complaint response: {response_text[:100]}...")
            return response_text
            
        except Exception as e:
            self.logger.error(f"[ResponseGenerator] Error generating complaint response: {e}")
            return (
                f"I'm sorry to hear about this issue. "
                f"I've registered your complaint (ID #{complaint_data.get('complaint_id')}). "
                f"Our support team will contact you within {complaint_data.get('sla_response_hours')} hour(s)."
            )
    
    def _build_context(
        self,
        conversation_history: Optional[List[Dict[str, str]]],
        user_name: Optional[str]
    ) -> str:
        """
        Build context string from conversation history and user name
        
        Args:
            conversation_history: Previous conversation messages
            user_name: User's first name
            
        Returns:
            Formatted context string
        """
        context_parts = []
        
        if user_name:
            context_parts.append(f"USER'S NAME: {user_name}")
        
        if conversation_history and len(conversation_history) > 0:
            # Include last 3 messages for context
            recent_history = conversation_history[-3:]
            history_text = "\n".join([
                f"{msg.get('role', 'user').upper()}: {msg.get('message', '')}"
                for msg in recent_history
            ])
            context_parts.append(f"RECENT CONVERSATION:\n{history_text}")
        
        return "\n\n".join(context_parts) if context_parts else "No previous context."

