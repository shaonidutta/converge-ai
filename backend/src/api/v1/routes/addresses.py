"""
Address Routes (Thin Controllers)
Address management
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, List

from src.core.database.connection import get_db
from src.core.security.dependencies import get_current_user
from src.core.models import User
from src.schemas.customer import (
    AddressRequest,
    AddressResponse,
)
from src.schemas.auth import MessageResponse
from src.services import AddressService

router = APIRouter(prefix="/addresses", tags=["Addresses"])


@router.get(
    "",
    response_model=List[AddressResponse],
    summary="List addresses"
)
async def list_addresses(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    active_only: bool = Query(True, description="Show only active addresses")
):
    """List user's addresses"""
    import logging
    import traceback
    logger = logging.getLogger(__name__)

    try:
        logger.info(f"List addresses request for user_id: {current_user.id}, active_only: {active_only}")
        address_service = AddressService(db)
        logger.debug("AddressService instantiated")

        result = await address_service.list_addresses(current_user, active_only)
        logger.info(f"Addresses fetched successfully for user_id: {current_user.id}, count: {len(result)}")
        return result
    except Exception as e:
        logger.error(f"Failed to fetch addresses - Exception: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch addresses: {str(e)}"
        )


@router.post(
    "",
    response_model=AddressResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add address"
)
async def add_address(
    request: AddressRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Add a new address"""
    import logging
    import traceback
    logger = logging.getLogger(__name__)

    try:
        logger.info(f"Add address request for user_id: {current_user.id}")
        logger.debug(f"Address data: {request.model_dump()}")

        address_service = AddressService(db)
        logger.debug("AddressService instantiated")

        result = await address_service.add_address(request, current_user)
        logger.info(f"Address added successfully for user_id: {current_user.id}, address_id: {result.id}")
        return result
    except Exception as e:
        logger.error(f"Failed to add address - Exception: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add address: {str(e)}"
        )


@router.get(
    "/{address_id}",
    response_model=AddressResponse,
    summary="Get address"
)
async def get_address(
    address_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Get address by ID"""
    try:
        address_service = AddressService(db)
        return await address_service.get_address(address_id, current_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch address"
        )


@router.put(
    "/{address_id}",
    response_model=AddressResponse,
    summary="Update address"
)
async def update_address(
    address_id: int,
    request: AddressRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Update address"""
    try:
        address_service = AddressService(db)
        return await address_service.update_address(address_id, request, current_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update address"
        )


@router.delete(
    "/{address_id}",
    response_model=MessageResponse,
    summary="Delete address"
)
async def delete_address(
    address_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Delete address (soft delete)"""
    try:
        address_service = AddressService(db)
        await address_service.delete_address(address_id, current_user)
        return MessageResponse(message="Address deleted successfully")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete address"
        )

