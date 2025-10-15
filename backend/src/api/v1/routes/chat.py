"""
Chat Routes (Thin Controllers)
Chat API endpoints for customer chatbot
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, List
import logging
import traceback

from src.core.database.connection import get_db
from src.core.security.dependencies import get_current_user
from src.core.models import User
from src.schemas.chat import (
    ChatMessageRequest,
    ChatMessageResponse,
    ChatHistoryResponse,
    SessionResponse,
)
from src.schemas.auth import MessageResponse
from src.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["Chat"])
logger = logging.getLogger(__name__)


@router.post(
    "/message",
    response_model=ChatMessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Send chat message"
)
async def send_message(
    request: ChatMessageRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Send a chat message and get AI response
    
    - **message**: User message text (required)
    - **session_id**: Session ID to continue conversation (optional, creates new if not provided)
    - **channel**: Communication channel (web, mobile, whatsapp)
    
    Returns:
    - User message stored in database
    - AI assistant response
    - Session ID for continuing conversation
    - Response time in milliseconds
    """
    try:
        logger.info(f"Chat message request: user_id={current_user.id}, session_id={request.session_id}")
        logger.debug(f"Message: {request.message[:100]}...")  # Log first 100 chars
        
        chat_service = ChatService(db)
        result = await chat_service.send_message(current_user, request)
        
        logger.info(f"Chat message processed: session_id={result.session_id}, response_time={result.response_time_ms}ms")
        return result
    except ValueError as e:
        logger.warning(f"Chat message failed - ValueError: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Chat message failed - Exception: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process message"
        )


@router.get(
    "/history/{session_id}",
    response_model=ChatHistoryResponse,
    summary="Get chat history"
)
async def get_history(
    session_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = Query(50, ge=1, le=200, description="Number of messages to retrieve"),
    skip: int = Query(0, ge=0, description="Number of messages to skip")
):
    """
    Get chat history for a specific session
    
    - **session_id**: Session ID (required)
    - **limit**: Maximum number of messages to retrieve (default: 50, max: 200)
    - **skip**: Number of messages to skip for pagination (default: 0)
    
    Returns:
    - List of messages in chronological order
    - Total message count
    """
    try:
        logger.info(f"Get chat history: user_id={current_user.id}, session_id={session_id}")
        
        chat_service = ChatService(db)
        result = await chat_service.get_history(current_user, session_id, limit, skip)
        
        logger.info(f"Chat history retrieved: {len(result.messages)} messages")
        return result
    except ValueError as e:
        logger.warning(f"Get chat history failed - ValueError: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Get chat history failed - Exception: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch history"
        )


@router.get(
    "/sessions",
    response_model=List[SessionResponse],
    summary="List chat sessions"
)
async def list_sessions(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    List all chat sessions for the current user
    
    Returns:
    - List of sessions ordered by most recent first
    - Each session includes:
      * session_id
      * message_count
      * last_message_at
      * first_message_at
    """
    try:
        logger.info(f"List chat sessions: user_id={current_user.id}")
        
        chat_service = ChatService(db)
        result = await chat_service.list_sessions(current_user)
        
        logger.info(f"Chat sessions retrieved: {len(result)} sessions")
        return result
    except Exception as e:
        logger.error(f"List chat sessions failed - Exception: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch sessions"
        )


@router.delete(
    "/sessions/{session_id}",
    response_model=MessageResponse,
    summary="Delete chat session"
)
async def delete_session(
    session_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Delete a chat session and all its messages
    
    - **session_id**: Session ID to delete (required)
    
    Returns:
    - Success message
    
    Note: This action is irreversible. All messages in the session will be permanently deleted.
    """
    try:
        logger.info(f"Delete chat session: user_id={current_user.id}, session_id={session_id}")
        
        chat_service = ChatService(db)
        await chat_service.delete_session(current_user, session_id)
        
        logger.info(f"Chat session deleted: session_id={session_id}")
        return MessageResponse(message="Session deleted successfully")
    except ValueError as e:
        logger.warning(f"Delete chat session failed - ValueError: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Delete chat session failed - Exception: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete session"
        )

