"""
Service Category Validation Service

Handles validation of service types and determines when subcategory selection is required.
"""

import logging
from typing import Dict, List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from src.core.models.category import Category, Subcategory
from src.core.models.rate_card import RateCard
from src.utils.entity_normalizer import normalize_service_type

logger = logging.getLogger(__name__)


class ServiceCategoryValidationResult:
    """Result of service category validation"""
    
    def __init__(
        self,
        is_valid: bool,
        requires_subcategory_selection: bool = False,
        available_subcategories: List[Dict[str, Any]] = None,
        default_rate_card_id: Optional[int] = None,
        error_message: Optional[str] = None,
        normalized_service_type: Optional[str] = None
    ):
        self.is_valid = is_valid
        self.requires_subcategory_selection = requires_subcategory_selection
        self.available_subcategories = available_subcategories or []
        self.default_rate_card_id = default_rate_card_id
        self.error_message = error_message
        self.normalized_service_type = normalized_service_type


class ServiceCategoryValidator:
    """
    Validates service types and determines subcategory requirements
    
    Features:
    - Checks if service type exists
    - Determines if subcategory selection is required
    - Returns available subcategories with pricing
    - Provides default rate card for single-option services
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def validate_service_type(self, service_type: str) -> ServiceCategoryValidationResult:
        """
        Validate service type and determine subcategory requirements
        
        Args:
            service_type: Raw service type from user input (e.g., "painting", "plumbing")
            
        Returns:
            ServiceCategoryValidationResult with validation details
        """
        try:
            logger.info(f"[ServiceCategoryValidator] Validating service type: '{service_type}'")
            
            # Normalize service type
            normalized = normalize_service_type(service_type)
            if not normalized:
                return ServiceCategoryValidationResult(
                    is_valid=False,
                    error_message=f"Unknown service type: {service_type}"
                )
            
            logger.info(f"[ServiceCategoryValidator] Normalized service type: '{normalized}'")

            # Convert underscores to spaces for database matching
            # e.g., "appliance_repair" → "appliance repair", "tv_repair" → "tv repair"
            search_term = normalized.replace('_', ' ')

            # First, check if this is a specific subcategory (e.g., "tv repair", "ac repair")
            subcategory_result = await self.db.execute(
                select(Subcategory)
                .where(
                    func.lower(Subcategory.name).like(f"%{search_term}%"),
                    Subcategory.is_active == True
                )
                .options(selectinload(Subcategory.category))
            )
            subcategory = subcategory_result.scalar_one_or_none()

            if subcategory:
                # Found a specific subcategory - check if it has rate cards
                rate_cards_result = await self.db.execute(
                    select(RateCard)
                    .where(
                        RateCard.subcategory_id == subcategory.id,
                        RateCard.is_active == True
                    )
                    .order_by(RateCard.price)
                )
                rate_cards = rate_cards_result.scalars().all()

                if rate_cards:
                    logger.info(f"[ServiceCategoryValidator] Found specific subcategory: {subcategory.name} with {len(rate_cards)} rate cards")
                    # Return the default (cheapest) rate card
                    default_rate_card = rate_cards[0]
                    return ServiceCategoryValidationResult(
                        is_valid=True,
                        requires_subcategory_selection=False,
                        normalized_service_type=normalized,
                        default_rate_card_id=default_rate_card.id
                    )

            # Not a specific subcategory, search for category
            category_result = await self.db.execute(
                select(Category)
                .where(
                    func.lower(Category.name).like(f"%{search_term}%"),
                    Category.is_active == True
                )
                .options(selectinload(Category.subcategories))
            )
            category = category_result.scalar_one_or_none()

            if not category:
                return ServiceCategoryValidationResult(
                    is_valid=False,
                    error_message=f"Service category '{service_type}' not found"
                )
            
            logger.info(f"[ServiceCategoryValidator] Found category: {category.name} (ID: {category.id})")
            
            # Get active subcategories with rate cards
            subcategories_result = await self.db.execute(
                select(Subcategory, func.count(RateCard.id).label('rate_card_count'))
                .outerjoin(RateCard, Subcategory.id == RateCard.subcategory_id)
                .where(
                    Subcategory.category_id == category.id,
                    Subcategory.is_active == True
                )
                .group_by(Subcategory.id)
                .order_by(Subcategory.display_order, Subcategory.name)
            )
            subcategories_data = subcategories_result.all()
            
            if not subcategories_data:
                return ServiceCategoryValidationResult(
                    is_valid=False,
                    error_message=f"No active subcategories found for {service_type}"
                )
            
            # Filter subcategories that have rate cards
            valid_subcategories = [(subcat, count) for subcat, count in subcategories_data if count > 0]
            
            if not valid_subcategories:
                return ServiceCategoryValidationResult(
                    is_valid=False,
                    error_message=f"No services available for {service_type}"
                )
            
            logger.info(f"[ServiceCategoryValidator] Found {len(valid_subcategories)} valid subcategories")
            
            # If only one subcategory, get the default rate card
            if len(valid_subcategories) == 1:
                subcategory = valid_subcategories[0][0]
                
                # Get the first active rate card for this subcategory
                rate_card_result = await self.db.execute(
                    select(RateCard)
                    .where(
                        RateCard.subcategory_id == subcategory.id,
                        RateCard.is_active == True
                    )
                    .order_by(RateCard.price)  # Get cheapest option as default
                    .limit(1)
                )
                default_rate_card = rate_card_result.scalar_one_or_none()
                
                return ServiceCategoryValidationResult(
                    is_valid=True,
                    requires_subcategory_selection=False,
                    default_rate_card_id=default_rate_card.id if default_rate_card else None,
                    normalized_service_type=normalized
                )
            
            # Multiple subcategories - need user selection
            available_subcategories = []
            for subcategory, rate_card_count in valid_subcategories:
                # Get rate cards for this subcategory
                rate_cards_result = await self.db.execute(
                    select(RateCard)
                    .where(
                        RateCard.subcategory_id == subcategory.id,
                        RateCard.is_active == True
                    )
                    .order_by(RateCard.price)
                )
                rate_cards = rate_cards_result.scalars().all()
                
                subcategory_info = {
                    "id": subcategory.id,
                    "name": subcategory.name,
                    "description": subcategory.description,
                    "rate_cards": [
                        {
                            "id": rc.id,
                            "name": rc.name,
                            "price": float(rc.price),
                            "strike_price": float(rc.strike_price) if rc.strike_price else None,
                            "description": rc.description
                        }
                        for rc in rate_cards
                    ]
                }
                available_subcategories.append(subcategory_info)
            
            return ServiceCategoryValidationResult(
                is_valid=True,
                requires_subcategory_selection=True,
                available_subcategories=available_subcategories,
                normalized_service_type=normalized
            )
            
        except Exception as e:
            logger.error(f"[ServiceCategoryValidator] Error validating service type '{service_type}': {e}", exc_info=True)
            return ServiceCategoryValidationResult(
                is_valid=False,
                error_message=f"Error validating service type: {str(e)}"
            )
    
    async def validate_subcategory_selection(
        self, 
        service_type: str, 
        subcategory_input: str
    ) -> ServiceCategoryValidationResult:
        """
        Validate user's subcategory selection
        
        Args:
            service_type: The main service type (e.g., "painting")
            subcategory_input: User's subcategory selection (e.g., "interior painting")
            
        Returns:
            ServiceCategoryValidationResult with selected rate card
        """
        try:
            logger.info(f"[ServiceCategoryValidator] Validating subcategory selection: '{subcategory_input}' for service '{service_type}'")
            
            # First validate the main service type
            service_validation = await self.validate_service_type(service_type)
            if not service_validation.is_valid:
                return service_validation
            
            # Search for matching subcategory/rate card
            subcategory_lower = subcategory_input.lower().strip()
            
            # Try to find matching rate card by name
            for subcategory_info in service_validation.available_subcategories:
                for rate_card in subcategory_info["rate_cards"]:
                    rate_card_name_lower = rate_card["name"].lower()
                    subcategory_name_lower = subcategory_info["name"].lower()
                    
                    # Check if user input matches rate card name or subcategory name
                    if (subcategory_lower in rate_card_name_lower or 
                        rate_card_name_lower in subcategory_lower or
                        subcategory_lower in subcategory_name_lower or
                        subcategory_name_lower in subcategory_lower):
                        
                        logger.info(f"[ServiceCategoryValidator] Found matching rate card: {rate_card['name']} (ID: {rate_card['id']})")
                        
                        return ServiceCategoryValidationResult(
                            is_valid=True,
                            requires_subcategory_selection=False,
                            default_rate_card_id=rate_card["id"],
                            normalized_service_type=service_validation.normalized_service_type
                        )
            
            # No match found
            available_options = []
            for subcategory_info in service_validation.available_subcategories:
                for rate_card in subcategory_info["rate_cards"]:
                    available_options.append(rate_card["name"])
            
            return ServiceCategoryValidationResult(
                is_valid=False,
                error_message=f"'{subcategory_input}' is not available. Available options: {', '.join(available_options[:3])}..."
            )
            
        except Exception as e:
            logger.error(f"[ServiceCategoryValidator] Error validating subcategory selection: {e}", exc_info=True)
            return ServiceCategoryValidationResult(
                is_valid=False,
                error_message=f"Error validating subcategory selection: {str(e)}"
            )


# Export
__all__ = ["ServiceCategoryValidator", "ServiceCategoryValidationResult"]
