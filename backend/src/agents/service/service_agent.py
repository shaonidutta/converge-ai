"""
ServiceAgent - Handles service discovery, search, and recommendations

This agent helps users:
- Browse categories and subcategories
- Search for services
- Get service details
- Get service recommendations
"""

import logging
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_, func
from decimal import Decimal

from src.core.models import User, Category, Subcategory, RateCard, Provider
from src.services.category_service import CategoryService

logger = logging.getLogger(__name__)


class ServiceAgent:
    """
    ServiceAgent - Specialist agent for service discovery and recommendations
    
    Handles:
    - Browsing categories, subcategories, and services
    - Searching services with filters
    - Getting service details
    - Recommending services based on user needs
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize ServiceAgent
        
        Args:
            db: Database session
        """
        self.db = db
        self.category_service = CategoryService(db)
        logger.info("ServiceAgent initialized")
    
    async def execute(
        self,
        intent: str,
        entities: Dict[str, Any],
        user: User,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Main execution method - routes to appropriate handler based on action
        
        Args:
            intent: Intent type (should be "service_inquiry")
            entities: Extracted entities from slot-filling
                {
                    "action": "browse_categories" | "browse_subcategories" | "browse_services" | 
                              "search" | "details" | "recommend",
                    "category_id": 1 (optional),
                    "subcategory_id": 1 (optional),
                    "rate_card_id": 1 (optional),
                    "query": "ac repair" (optional),
                    "max_price": 1000 (optional),
                    "min_price": 500 (optional)
                }
            user: Current authenticated user
            session_id: Chat session ID
        
        Returns:
            Response dict with service information
        """
        logger.info(f"ServiceAgent.execute called: intent={intent}, action={entities.get('action')}, user_id={user.id}")
        
        try:
            # Get action from entities
            action = entities.get("action", "browse_categories")
            
            # Route to appropriate method
            if action == "browse_categories":
                return await self._browse_categories(entities, user)
            elif action == "browse_subcategories":
                return await self._browse_subcategories(entities, user)
            elif action == "browse_services":
                return await self._browse_services(entities, user)
            elif action == "search":
                return await self._search_services(entities, user)
            elif action == "details":
                return await self._get_service_details(entities, user)
            elif action == "recommend":
                return await self._recommend_services(entities, user)
            else:
                logger.warning(f"Unknown action: {action}")
                return {
                    "response": f"I'm not sure how to help with '{action}'. "
                               f"I can help you browse services, search, or get recommendations.",
                    "action_taken": "unknown_action",
                    "metadata": {"action": action}
                }
        
        except Exception as e:
            logger.error(f"Error in ServiceAgent.execute: {str(e)}", exc_info=True)
            return {
                "response": "❌ Sorry, I encountered an error while processing your request. Please try again.",
                "action_taken": "error",
                "metadata": {"error": str(e)}
            }
    
    async def _browse_categories(self, entities: Dict[str, Any], user: User) -> Dict[str, Any]:
        """
        Browse all available service categories
        
        Args:
            entities: Extracted entities (none required)
            user: Current user
        
        Returns:
            Response dict with categories list
        """
        try:
            logger.info(f"Browsing categories for user_id={user.id}")
            
            # Get categories from CategoryService
            categories = await self.category_service.list_categories(skip=0, limit=50)
            
            if not categories:
                return {
                    "response": "No service categories are currently available. Please check back later.",
                    "action_taken": "no_categories",
                    "metadata": {}
                }
            
            # Format response
            response_lines = ["Here are our service categories:\n"]
            for idx, cat in enumerate(categories, 1):
                subcat_text = f"({cat.subcategory_count} subcategories)" if cat.subcategory_count > 0 else "(no subcategories)"
                response_lines.append(f"{idx}. {cat.name} {subcat_text}")
            
            response_lines.append("\nWhich category would you like to explore?")
            
            return {
                "response": "\n".join(response_lines),
                "action_taken": "categories_listed",
                "metadata": {
                    "categories": [
                        {
                            "id": cat.id,
                            "name": cat.name,
                            "subcategory_count": cat.subcategory_count
                        }
                        for cat in categories
                    ]
                }
            }
        
        except Exception as e:
            logger.error(f"Error browsing categories: {str(e)}")
            return {
                "response": f"❌ Failed to load categories: {str(e)}",
                "action_taken": "error",
                "metadata": {"error": str(e)}
            }
    
    async def _browse_subcategories(self, entities: Dict[str, Any], user: User) -> Dict[str, Any]:
        """
        Browse subcategories under a category
        
        Args:
            entities: Must contain category_id
            user: Current user
        
        Returns:
            Response dict with subcategories list
        """
        try:
            # Validate category_id
            category_id = entities.get("category_id")
            if not category_id:
                return {
                    "response": "I need to know which category you're interested in. Could you specify the category?",
                    "action_taken": "missing_entity",
                    "metadata": {"missing": "category_id"}
                }
            
            logger.info(f"Browsing subcategories for category_id={category_id}, user_id={user.id}")
            
            # Get subcategories from CategoryService
            subcategories = await self.category_service.list_subcategories(int(category_id), skip=0, limit=50)
            
            if not subcategories:
                return {
                    "response": "No subcategories found for this category.",
                    "action_taken": "no_subcategories",
                    "metadata": {"category_id": category_id}
                }
            
            # Format response
            category_name = subcategories[0].category_name if subcategories else "this category"
            response_lines = [f"{category_name} has these subcategories:\n"]
            for idx, subcat in enumerate(subcategories, 1):
                service_text = f"({subcat.rate_card_count} services)" if subcat.rate_card_count > 0 else "(no services)"
                response_lines.append(f"{idx}. {subcat.name} {service_text}")
            
            response_lines.append("\nWhich subcategory would you like to see?")
            
            return {
                "response": "\n".join(response_lines),
                "action_taken": "subcategories_listed",
                "metadata": {
                    "category_id": category_id,
                    "category_name": category_name,
                    "subcategories": [
                        {
                            "id": subcat.id,
                            "name": subcat.name,
                            "rate_card_count": subcat.rate_card_count
                        }
                        for subcat in subcategories
                    ]
                }
            }
        
        except ValueError as e:
            return {
                "response": f"❌ {str(e)}",
                "action_taken": "error",
                "metadata": {"error": str(e)}
            }
        except Exception as e:
            logger.error(f"Error browsing subcategories: {str(e)}")
            return {
                "response": f"❌ Failed to load subcategories: {str(e)}",
                "action_taken": "error",
                "metadata": {"error": str(e)}
            }
    
    async def _browse_services(self, entities: Dict[str, Any], user: User) -> Dict[str, Any]:
        """
        Browse services (rate cards) under a subcategory
        
        Args:
            entities: Must contain subcategory_id
            user: Current user
        
        Returns:
            Response dict with services list
        """
        try:
            # Validate subcategory_id
            subcategory_id = entities.get("subcategory_id")
            if not subcategory_id:
                return {
                    "response": "I need to know which subcategory you're interested in. Could you specify it?",
                    "action_taken": "missing_entity",
                    "metadata": {"missing": "subcategory_id"}
                }
            
            logger.info(f"Browsing services for subcategory_id={subcategory_id}, user_id={user.id}")
            
            # Get rate cards from CategoryService
            rate_cards = await self.category_service.list_rate_cards(int(subcategory_id), skip=0, limit=50)
            
            if not rate_cards:
                return {
                    "response": "No services found for this subcategory.",
                    "action_taken": "no_services",
                    "metadata": {"subcategory_id": subcategory_id}
                }
            
            # Format response
            response_lines = ["Here are the available services:\n"]
            for idx, rc in enumerate(rate_cards, 1):
                price_text = f"₹{rc.price:,.2f}"
                if rc.strike_price:
                    price_text = f"₹{rc.price:,.2f} (was ₹{rc.strike_price:,.2f})"
                response_lines.append(f"{idx}. {rc.name} - {price_text}")
            
            response_lines.append("\nWould you like details on any service, or shall I help you book one?")
            
            return {
                "response": "\n".join(response_lines),
                "action_taken": "services_listed",
                "metadata": {
                    "subcategory_id": subcategory_id,
                    "services": [
                        {
                            "id": rc.id,
                            "name": rc.name,
                            "price": float(rc.price),
                            "strike_price": float(rc.strike_price) if rc.strike_price else None
                        }
                        for rc in rate_cards
                    ]
                }
            }
        
        except ValueError as e:
            return {
                "response": f"❌ {str(e)}",
                "action_taken": "error",
                "metadata": {"error": str(e)}
            }
        except Exception as e:
            logger.error(f"Error browsing services: {str(e)}")
            return {
                "response": f"❌ Failed to load services: {str(e)}",
                "action_taken": "error",
                "metadata": {"error": str(e)}
            }

    async def _search_services(self, entities: Dict[str, Any], user: User) -> Dict[str, Any]:
        """
        Search for services by keyword with optional filters

        Args:
            entities: Must contain query, optional: max_price, min_price, category_id
            user: Current user

        Returns:
            Response dict with search results
        """
        try:
            # Validate query
            query = entities.get("query")
            if not query:
                return {
                    "response": "What service are you looking for? Please tell me what you need.",
                    "action_taken": "missing_entity",
                    "metadata": {"missing": "query"}
                }

            logger.info(f"Searching services: query='{query}', user_id={user.id}")

            # Build search query
            search_query = select(RateCard).where(RateCard.is_active == True)

            # Add text search (name or description)
            search_pattern = f"%{query}%"
            search_query = search_query.where(
                or_(
                    RateCard.name.ilike(search_pattern),
                    RateCard.description.ilike(search_pattern)
                )
            )

            # Add price filters if provided
            max_price = entities.get("max_price")
            if max_price:
                search_query = search_query.where(RateCard.price <= Decimal(str(max_price)))

            min_price = entities.get("min_price")
            if min_price:
                search_query = search_query.where(RateCard.price >= Decimal(str(min_price)))

            # Add category filter if provided
            category_id = entities.get("category_id")
            if category_id:
                search_query = search_query.where(RateCard.category_id == int(category_id))

            # Execute query
            search_query = search_query.order_by(RateCard.price).limit(20)
            result = await self.db.execute(search_query)
            rate_cards = result.scalars().all()

            if not rate_cards:
                filter_text = ""
                if max_price:
                    filter_text += f" under ₹{max_price}"
                if min_price:
                    filter_text += f" above ₹{min_price}"

                return {
                    "response": f"No services found matching '{query}'{filter_text}. "
                               f"Try a different search term or browse our categories.",
                    "action_taken": "no_results",
                    "metadata": {
                        "query": query,
                        "filters": {
                            "max_price": max_price,
                            "min_price": min_price,
                            "category_id": category_id
                        }
                    }
                }

            # Format response
            filter_text = ""
            if max_price or min_price:
                if max_price and min_price:
                    filter_text = f" (₹{min_price} - ₹{max_price})"
                elif max_price:
                    filter_text = f" (under ₹{max_price})"
                else:
                    filter_text = f" (above ₹{min_price})"

            response_lines = [f"Found {len(rate_cards)} services matching '{query}'{filter_text}:\n"]
            for idx, rc in enumerate(rate_cards[:10], 1):  # Show top 10
                price_text = f"₹{rc.price:,.2f}"
                if rc.strike_price:
                    price_text = f"₹{rc.price:,.2f} (was ₹{rc.strike_price:,.2f})"
                response_lines.append(f"{idx}. {rc.name} - {price_text}")

            if len(rate_cards) > 10:
                response_lines.append(f"\n...and {len(rate_cards) - 10} more services.")

            response_lines.append("\nWould you like details on any service?")

            return {
                "response": "\n".join(response_lines),
                "action_taken": "services_found",
                "metadata": {
                    "query": query,
                    "filters": {
                        "max_price": max_price,
                        "min_price": min_price,
                        "category_id": category_id
                    },
                    "results_count": len(rate_cards),
                    "services": [
                        {
                            "id": rc.id,
                            "name": rc.name,
                            "price": float(rc.price),
                            "strike_price": float(rc.strike_price) if rc.strike_price else None
                        }
                        for rc in rate_cards
                    ]
                }
            }

        except Exception as e:
            logger.error(f"Error searching services: {str(e)}")
            return {
                "response": f"❌ Failed to search services: {str(e)}",
                "action_taken": "error",
                "metadata": {"error": str(e)}
            }

    async def _get_service_details(self, entities: Dict[str, Any], user: User) -> Dict[str, Any]:
        """
        Get detailed information about a specific service

        Args:
            entities: Must contain rate_card_id
            user: Current user

        Returns:
            Response dict with service details
        """
        try:
            # Validate rate_card_id
            rate_card_id = entities.get("rate_card_id")
            if not rate_card_id:
                return {
                    "response": "Which service would you like to know more about? Please specify the service.",
                    "action_taken": "missing_entity",
                    "metadata": {"missing": "rate_card_id"}
                }

            logger.info(f"Getting service details: rate_card_id={rate_card_id}, user_id={user.id}")

            # Get rate card with relationships
            result = await self.db.execute(
                select(RateCard, Category, Subcategory, Provider)
                .join(Category, RateCard.category_id == Category.id)
                .join(Subcategory, RateCard.subcategory_id == Subcategory.id)
                .join(Provider, RateCard.provider_id == Provider.id)
                .where(RateCard.id == int(rate_card_id), RateCard.is_active == True)
            )
            data = result.one_or_none()

            if not data:
                return {
                    "response": "❌ Service not found or no longer available.",
                    "action_taken": "not_found",
                    "metadata": {"rate_card_id": rate_card_id}
                }

            rate_card, category, subcategory, provider = data

            # Format response
            response_lines = [
                f"📋 {rate_card.name}",
                f"",
                f"💰 Price: ₹{rate_card.price:,.2f}"
            ]

            if rate_card.strike_price:
                discount = ((rate_card.strike_price - rate_card.price) / rate_card.strike_price) * 100
                response_lines.append(f"   (Save ₹{rate_card.strike_price - rate_card.price:,.2f} - {discount:.0f}% off!)")

            response_lines.append(f"")

            if rate_card.description:
                response_lines.append(f"📝 Description:")
                response_lines.append(f"{rate_card.description}")
                response_lines.append(f"")

            response_lines.extend([
                f"📂 Category: {category.name}",
                f"🏷️ Subcategory: {subcategory.name}",
                f"👤 Provider: {provider.first_name} {provider.last_name or ''}",
                f"⭐ Rating: {provider.avg_rating}/5.0 ({provider.total_bookings} bookings)",
                f"",
                f"Would you like to book this service?"
            ])

            return {
                "response": "\n".join(response_lines),
                "action_taken": "service_details_shown",
                "metadata": {
                    "rate_card_id": rate_card.id,
                    "service": {
                        "id": rate_card.id,
                        "name": rate_card.name,
                        "description": rate_card.description,
                        "price": float(rate_card.price),
                        "strike_price": float(rate_card.strike_price) if rate_card.strike_price else None,
                        "category": category.name,
                        "subcategory": subcategory.name,
                        "provider": {
                            "name": f"{provider.first_name} {provider.last_name or ''}",
                            "rating": float(provider.avg_rating),
                            "total_bookings": provider.total_bookings
                        }
                    }
                }
            }

        except ValueError as e:
            return {
                "response": f"❌ {str(e)}",
                "action_taken": "error",
                "metadata": {"error": str(e)}
            }
        except Exception as e:
            logger.error(f"Error getting service details: {str(e)}")
            return {
                "response": f"❌ Failed to load service details: {str(e)}",
                "action_taken": "error",
                "metadata": {"error": str(e)}
            }

    async def _recommend_services(self, entities: Dict[str, Any], user: User) -> Dict[str, Any]:
        """
        Recommend services based on user's problem/need

        Args:
            entities: Must contain query (user's problem/need)
            user: Current user

        Returns:
            Response dict with recommendations
        """
        try:
            # Validate query
            query = entities.get("query")
            if not query:
                return {
                    "response": "What problem are you trying to solve? Tell me what you need help with.",
                    "action_taken": "missing_entity",
                    "metadata": {"missing": "query"}
                }

            logger.info(f"Recommending services: query='{query}', user_id={user.id}")

            # Simple keyword-based recommendation (can be enhanced with LLM later)
            # Search in name and description
            search_pattern = f"%{query}%"
            result = await self.db.execute(
                select(RateCard)
                .where(
                    and_(
                        RateCard.is_active == True,
                        or_(
                            RateCard.name.ilike(search_pattern),
                            RateCard.description.ilike(search_pattern)
                        )
                    )
                )
                .order_by(RateCard.price)
                .limit(5)
            )
            recommendations = result.scalars().all()

            if not recommendations:
                return {
                    "response": f"I couldn't find specific recommendations for '{query}'. "
                               f"Could you try describing your problem differently, or browse our categories?",
                    "action_taken": "no_recommendations",
                    "metadata": {"query": query}
                }

            # Format response
            response_lines = [f"For '{query}', I recommend:\n"]
            for idx, rc in enumerate(recommendations, 1):
                price_text = f"₹{rc.price:,.2f}"
                if rc.strike_price:
                    price_text = f"₹{rc.price:,.2f} (was ₹{rc.strike_price:,.2f})"
                response_lines.append(f"{idx}. {rc.name} - {price_text}")

            response_lines.append("\nWould you like to book one of these services?")

            return {
                "response": "\n".join(response_lines),
                "action_taken": "services_recommended",
                "metadata": {
                    "query": query,
                    "recommendations": [
                        {
                            "id": rc.id,
                            "name": rc.name,
                            "price": float(rc.price),
                            "strike_price": float(rc.strike_price) if rc.strike_price else None
                        }
                        for rc in recommendations
                    ]
                }
            }

        except Exception as e:
            logger.error(f"Error recommending services: {str(e)}")
            return {
                "response": f"❌ Failed to get recommendations: {str(e)}",
                "action_taken": "error",
                "metadata": {"error": str(e)}
            }


# Export
__all__ = ["ServiceAgent"]


