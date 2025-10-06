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
    try:
        address_service = AddressService(db)
        return await address_service.list_addresses(current_user, active_only)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch addresses"
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
    try:
        address_service = AddressService(db)
        return await address_service.add_address(request, current_user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add address"
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

