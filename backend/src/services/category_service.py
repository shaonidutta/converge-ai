"""
Category Service
Business logic for category and subcategory management
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
import logging

from src.core.models import Category, Subcategory, RateCard
from src.schemas.customer import (
    CategoryResponse,
    SubcategoryResponse,
    RateCardResponse,
)

logger = logging.getLogger(__name__)


class CategoryService:
    """Service class for category management business logic"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def list_categories(
        self, 
        skip: int = 0, 
        limit: int = 50
    ) -> List[CategoryResponse]:
        """
        List all active categories with subcategory count
        
        Args:
            skip: Number of records to skip
            limit: Number of records to return
            
        Returns:
            List of CategoryResponse
        """
        # Get categories with subcategory count
        result = await self.db.execute(
            select(
                Category,
                func.count(Subcategory.id).label('subcategory_count')
            )
            .outerjoin(Subcategory, Category.id == Subcategory.category_id)
            .where(Category.is_active == True)
            .group_by(Category.id)
            .order_by(Category.display_order, Category.name)
            .offset(skip)
            .limit(limit)
        )
        categories = result.all()
        
        return [
            CategoryResponse(
                id=cat[0].id,
                name=cat[0].name,
                slug=cat[0].slug,
                description=cat[0].description,
                image=cat[0].image,
                is_active=cat[0].is_active,
                subcategory_count=cat[1]
            )
            for cat in categories
        ]
    
    async def get_category(self, category_id: int) -> CategoryResponse:
        """
        Get category by ID
        
        Args:
            category_id: Category ID
            
        Returns:
            CategoryResponse
            
        Raises:
            ValueError: If category not found
        """
        # Get category with subcategory count
        result = await self.db.execute(
            select(
                Category,
                func.count(Subcategory.id).label('subcategory_count')
            )
            .outerjoin(Subcategory, Category.id == Subcategory.category_id)
            .where(Category.id == category_id, Category.is_active == True)
            .group_by(Category.id)
        )
        category_data = result.one_or_none()
        
        if not category_data:
            raise ValueError("Category not found")
        
        cat, count = category_data
        
        return CategoryResponse(
            id=cat.id,
            name=cat.name,
            slug=cat.slug,
            description=cat.description,
            image=cat.image,
            is_active=cat.is_active,
            subcategory_count=count
        )
    
    async def list_subcategories(
        self,
        category_id: int,
        skip: int = 0,
        limit: int = 50
    ) -> List[SubcategoryResponse]:
        """
        List subcategories under a category
        
        Args:
            category_id: Category ID
            skip: Number of records to skip
            limit: Number of records to return
            
        Returns:
            List of SubcategoryResponse
            
        Raises:
            ValueError: If category not found
        """
        # Verify category exists
        category_result = await self.db.execute(
            select(Category).where(
                Category.id == category_id,
                Category.is_active == True
            )
        )
        category = category_result.scalar_one_or_none()
        
        if not category:
            raise ValueError("Category not found")
        
        # Get subcategories with rate card count
        result = await self.db.execute(
            select(
                Subcategory,
                func.count(RateCard.id).label('rate_card_count')
            )
            .outerjoin(RateCard, Subcategory.id == RateCard.subcategory_id)
            .where(
                Subcategory.category_id == category_id,
                Subcategory.is_active == True
            )
            .group_by(Subcategory.id)
            .order_by(Subcategory.display_order, Subcategory.name)
            .offset(skip)
            .limit(limit)
        )
        subcategories = result.all()
        
        return [
            SubcategoryResponse(
                id=subcat[0].id,
                name=subcat[0].name,
                slug=subcat[0].slug,
                description=subcat[0].description,
                category_id=subcat[0].category_id,
                category_name=category.name,
                is_active=subcat[0].is_active,
                rate_card_count=subcat[1]
            )
            for subcat in subcategories
        ]
    
    async def list_rate_cards(
        self,
        subcategory_id: int,
        skip: int = 0,
        limit: int = 50
    ) -> List[RateCardResponse]:
        """
        List rate cards under a subcategory
        
        Args:
            subcategory_id: Subcategory ID
            skip: Number of records to skip
            limit: Number of records to return
            
        Returns:
            List of RateCardResponse
            
        Raises:
            ValueError: If subcategory not found
        """
        # Verify subcategory exists
        subcategory_result = await self.db.execute(
            select(Subcategory).where(
                Subcategory.id == subcategory_id,
                Subcategory.is_active == True
            )
        )
        subcategory = subcategory_result.scalar_one_or_none()
        
        if not subcategory:
            raise ValueError("Subcategory not found")
        
        # Get rate cards
        result = await self.db.execute(
            select(RateCard)
            .where(
                RateCard.subcategory_id == subcategory_id,
                RateCard.is_active == True
            )
            .order_by(RateCard.name)
            .offset(skip)
            .limit(limit)
        )
        rate_cards = result.scalars().all()
        
        return [
            RateCardResponse(
                id=rc.id,
                name=rc.name,
                price=rc.price,
                strike_price=rc.strike_price,
                category_id=rc.category_id,
                subcategory_id=rc.subcategory_id,
                is_active=rc.is_active
            )
            for rc in rate_cards
        ]


# Export
__all__ = ["CategoryService"]

