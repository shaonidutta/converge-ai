"""
Category Routes (Thin Controllers)
Category and subcategory browsing
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, List

from src.core.database.connection import get_db
from src.schemas.customer import (
    CategoryResponse,
    SubcategoryResponse,
    RateCardResponse,
)
from src.services import CategoryService

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get(
    "",
    response_model=List[CategoryResponse],
    summary="List categories"
)
async def list_categories(
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """List all active categories"""
    try:
        category_service = CategoryService(db)
        return await category_service.list_categories(skip, limit)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch categories"
        )


@router.get(
    "/{category_id}",
    response_model=CategoryResponse,
    summary="Get category"
)
async def get_category(
    category_id: int,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Get category by ID"""
    try:
        category_service = CategoryService(db)
        return await category_service.get_category(category_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch category"
        )


@router.get(
    "/{category_id}/subcategories",
    response_model=List[SubcategoryResponse],
    summary="List subcategories"
)
async def list_subcategories(
    category_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """List subcategories under a category"""
    try:
        category_service = CategoryService(db)
        return await category_service.list_subcategories(category_id, skip, limit)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch subcategories"
        )


@router.get(
    "/subcategories/{subcategory_id}/rate-cards",
    response_model=List[RateCardResponse],
    summary="List rate cards"
)
async def list_rate_cards(
    subcategory_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """List rate cards under a subcategory"""
    try:
        category_service = CategoryService(db)
        return await category_service.list_rate_cards(subcategory_id, skip, limit)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch rate cards"
        )

