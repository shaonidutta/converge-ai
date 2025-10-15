"""
Repository for Priority Queue data access operations
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import joinedload

from src.core.models import PriorityQueue, User, Staff, IntentType


class PriorityQueueRepository:
    """
    Repository for priority queue data access
    
    Handles all database operations for priority queue items.
    Follows repository pattern for clean separation of concerns.
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize repository
        
        Args:
            db: Async database session
        """
        self.db = db
        self.logger = logging.getLogger(__name__)
    
    async def get_priority_items(
        self,
        filters: Dict[str, Any],
        sort_by: str = "priority_score",
        sort_order: str = "desc",
        skip: int = 0,
        limit: int = 20
    ) -> List[PriorityQueue]:
        """
        Get priority queue items with filters, sorting, and pagination
        
        Args:
            filters: Dictionary of filter conditions
            sort_by: Field to sort by (priority_score, created_at, confidence_score)
            sort_order: Sort order (asc, desc)
            skip: Number of items to skip (pagination offset)
            limit: Maximum number of items to return
        
        Returns:
            List of PriorityQueue model instances
        """
        try:
            # Build base query with eager loading of relationships
            query = select(PriorityQueue).options(
                joinedload(PriorityQueue.user),
                joinedload(PriorityQueue.reviewed_by_staff)
            )
            
            # Apply filters
            query = self._apply_filters(query, filters)
            
            # Apply sorting
            query = self._apply_sorting(query, sort_by, sort_order)
            
            # Apply pagination
            query = query.offset(skip).limit(limit)
            
            # Execute query
            result = await self.db.execute(query)
            items = result.scalars().unique().all()
            
            self.logger.info(
                f"Retrieved {len(items)} priority queue items "
                f"(skip={skip}, limit={limit}, filters={filters})"
            )
            
            return list(items)
            
        except Exception as e:
            self.logger.error(f"Error retrieving priority items: {e}", exc_info=True)
            raise
    
    async def count_priority_items(self, filters: Dict[str, Any]) -> int:
        """
        Count total priority queue items matching filters
        
        Args:
            filters: Dictionary of filter conditions
        
        Returns:
            Total count of matching items
        """
        try:
            # Build count query
            query = select(func.count(PriorityQueue.id))
            
            # Apply same filters as get_priority_items
            query = self._apply_filters(query, filters)
            
            # Execute query
            result = await self.db.execute(query)
            count = result.scalar()
            
            self.logger.info(f"Counted {count} priority queue items (filters={filters})")
            
            return count or 0
            
        except Exception as e:
            self.logger.error(f"Error counting priority items: {e}", exc_info=True)
            raise
    
    async def get_item_by_id(self, item_id: int) -> Optional[PriorityQueue]:
        """
        Get single priority queue item by ID
        
        Args:
            item_id: Priority queue item ID
        
        Returns:
            PriorityQueue instance or None if not found
        """
        try:
            query = select(PriorityQueue).options(
                joinedload(PriorityQueue.user),
                joinedload(PriorityQueue.reviewed_by_staff)
            ).where(PriorityQueue.id == item_id)
            
            result = await self.db.execute(query)
            item = result.scalar_one_or_none()
            
            if item:
                self.logger.info(f"Retrieved priority queue item {item_id}")
            else:
                self.logger.warning(f"Priority queue item {item_id} not found")
            
            return item
            
        except Exception as e:
            self.logger.error(f"Error retrieving priority item {item_id}: {e}", exc_info=True)
            raise
    
    def _apply_filters(self, query, filters: Dict[str, Any]):
        """
        Apply filters to query
        
        Args:
            query: SQLAlchemy query object
            filters: Dictionary of filter conditions
        
        Returns:
            Modified query with filters applied
        """
        # Filter by review status
        status = filters.get("status")
        if status == "pending":
            query = query.where(PriorityQueue.is_reviewed == False)
        elif status == "reviewed":
            query = query.where(PriorityQueue.is_reviewed == True)
        # 'all' or None - no filter
        
        # Filter by intent type
        intent_type = filters.get("intent_type")
        if intent_type:
            try:
                intent_enum = IntentType(intent_type)
                query = query.where(PriorityQueue.intent_type == intent_enum)
            except ValueError:
                self.logger.warning(f"Invalid intent_type: {intent_type}")
        
        # Filter by priority score range
        priority_min = filters.get("priority_min")
        if priority_min is not None:
            query = query.where(PriorityQueue.priority_score >= priority_min)
        
        priority_max = filters.get("priority_max")
        if priority_max is not None:
            query = query.where(PriorityQueue.priority_score <= priority_max)
        
        # Filter by date range
        date_from = filters.get("date_from")
        if date_from:
            query = query.where(PriorityQueue.created_at >= date_from)
        
        date_to = filters.get("date_to")
        if date_to:
            query = query.where(PriorityQueue.created_at <= date_to)
        
        return query
    
    def _apply_sorting(self, query, sort_by: str, sort_order: str):
        """
        Apply sorting to query
        
        Args:
            query: SQLAlchemy query object
            sort_by: Field to sort by
            sort_order: Sort order (asc, desc)
        
        Returns:
            Modified query with sorting applied
        """
        # Map sort field to model attribute
        sort_field_map = {
            "priority_score": PriorityQueue.priority_score,
            "created_at": PriorityQueue.created_at,
            "confidence_score": PriorityQueue.confidence_score,
            "updated_at": PriorityQueue.updated_at
        }
        
        sort_field = sort_field_map.get(sort_by, PriorityQueue.priority_score)
        
        # Apply sort order
        if sort_order.lower() == "asc":
            query = query.order_by(sort_field.asc())
        else:
            query = query.order_by(sort_field.desc())
        
        # Secondary sort by created_at for consistent ordering
        if sort_by != "created_at":
            query = query.order_by(PriorityQueue.created_at.desc())
        
        return query
    
    async def update_review_status(
        self,
        item_id: int,
        staff_id: int,
        action_taken: str
    ) -> Optional[PriorityQueue]:
        """
        Update review status of priority queue item
        
        Args:
            item_id: Priority queue item ID
            staff_id: Staff ID who reviewed
            action_taken: Description of action taken
        
        Returns:
            Updated PriorityQueue instance or None if not found
        """
        try:
            item = await self.get_item_by_id(item_id)
            
            if not item:
                return None
            
            # Update review status
            item.is_reviewed = True
            item.reviewed_by_staff_id = staff_id
            item.reviewed_at = datetime.now()
            item.action_taken = action_taken
            
            await self.db.commit()
            await self.db.refresh(item)
            
            self.logger.info(
                f"Updated review status for priority queue item {item_id} "
                f"by staff {staff_id}"
            )
            
            return item
            
        except Exception as e:
            self.logger.error(
                f"Error updating review status for item {item_id}: {e}",
                exc_info=True
            )
            await self.db.rollback()
            raise

