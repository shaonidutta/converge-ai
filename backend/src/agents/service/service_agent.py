"""
ServiceAgent - NLP-Enhanced service discovery with intelligent category matching

This agent helps users:
- Browse categories and subcategories with natural language understanding
- Search for services with spell correction and semantic matching
- Get service details with confidence-based responses
- Handle subcategory queries with intelligent category mapping
"""

import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_, func, text
from decimal import Decimal
import asyncio

# NLP imports
try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    from spellchecker import SpellChecker
    import numpy as np
    NLP_AVAILABLE = True
except ImportError:
    NLP_AVAILABLE = False
    logging.warning("NLP packages not available. Install sentence-transformers, scikit-learn, pyspellchecker for enhanced functionality.")

from src.core.models import User, Category, Subcategory, RateCard, Provider
from src.services.category_service import CategoryService
from src.services.response_generator import ResponseGenerator

logger = logging.getLogger(__name__)


class CategoryMatcher:
    """
    NLP-powered category matching with confidence scoring

    Handles:
    - Spell correction for typos
    - Semantic similarity matching
    - Fuzzy string matching
    - Confidence-based responses
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.spell_checker = SpellChecker() if NLP_AVAILABLE else None
        self.semantic_model = None
        self.categories_cache: List[Dict[str, Any]] = []
        self.cache_timestamp = None

        # Initialize semantic model if available
        if NLP_AVAILABLE:
            try:
                self.semantic_model = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("Semantic model loaded successfully")
            except Exception as e:
                logger.warning(f"Failed to load semantic model: {e}")
                self.semantic_model = None

    async def match_category(self, user_input: str) -> Optional[Dict]:
        """
        Multi-level NLP matching with confidence scoring

        Args:
            user_input: User's search term (e.g., "packers", "eletrician")

        Returns:
            Dict with category info and confidence score, or None if no match
            {
                "category": {"id": 12, "name": "Packers and Movers"},
                "confidence": 0.85,
                "method": "semantic",
                "original_input": "packers"
            }
        """
        if not user_input or not user_input.strip():
            return None

        user_input = user_input.strip().lower()
        results = []

        # Refresh categories cache if needed
        await self._refresh_categories_cache()

        if not self.categories_cache:
            return None

        # Level 1: Exact match
        exact_match = await self._exact_match(user_input)
        if exact_match:
            results.append({
                "category": exact_match,
                "confidence": 1.0,
                "method": "exact",
                "original_input": user_input
            })

        # Level 2: Spell correction + match
        if self.spell_checker:
            corrected = self.spell_checker.correction(user_input)
            if corrected and corrected != user_input:
                corrected_match = await self._exact_match(corrected)
                if corrected_match:
                    results.append({
                        "category": corrected_match,
                        "confidence": 0.8,
                        "method": "spell_corrected",
                        "original_input": user_input,
                        "corrected_to": corrected
                    })

        # Level 3: Fuzzy string matching
        fuzzy_matches = await self._fuzzy_match(user_input)
        results.extend(fuzzy_matches)

        # Level 4: Semantic similarity (if available)
        if self.semantic_model:
            semantic_matches = await self._semantic_match(user_input)
            results.extend(semantic_matches)

        # Sort by confidence and return best match
        if results:
            results.sort(key=lambda x: x["confidence"], reverse=True)
            return results[0]

        return None

    async def _refresh_categories_cache(self) -> None:
        """Refresh categories cache from database"""
        try:
            query = select(Category).where(Category.is_active == True)
            result = await self.db.execute(query)
            categories = result.scalars().all()

            self.categories_cache = [
                {"id": cat.id, "name": cat.name, "description": cat.description or ""}
                for cat in categories
            ]
            logger.info(f"Refreshed categories cache with {len(self.categories_cache)} categories")

        except Exception as e:
            logger.error(f"Failed to refresh categories cache: {e}")
            self.categories_cache = []

    async def _exact_match(self, input_text: str) -> Optional[Dict[str, Any]]:
        """Check for exact matches in category names"""
        if not self.categories_cache:
            return None

        # Special handling for compound terms and semantic variations
        special_mappings = {
            # Salon services
            "men salon": "Salon for Men",
            "male salon": "Salon for Men",
            "barber": "Salon for Men",
            "barber shop": "Salon for Men",
            "women salon": "Salon for Women",
            "female salon": "Salon for Women",
            "beauty salon": "Salon for Women",
            "beauty": "Salon for Women",

            # Car services
            "car care": "Car Care",
            "car service": "Car Care",
            "vehicle care": "Car Care",
            "auto care": "Car Care",

            # AC services
            "ac service": "Test AC Services",
            "ac repair": "Appliance Repair",
            "air conditioning": "Appliance Repair",
            "appliance": "Appliance Repair",

            # Moving services
            "packers": "Packers and Movers",
            "movers": "Packers and Movers",
            "moving": "Packers and Movers",
            "moving company": "Packers and Movers",
            "shifting": "Packers and Movers",
            "relocation": "Packers and Movers",
            "packing": "Packers and Movers",

            # Cleaning services
            "house cleaning": "Home Cleaning",
            "home cleaning": "Home Cleaning",
            "cleaning service": "Home Cleaning",
            "maid service": "Home Cleaning",

            # Other services
            "pest extermination": "Pest Control",
            "bug control": "Pest Control",
            "water filter": "Water Purifier",
            "ro service": "Water Purifier",
            "handyman": "Carpentry",
            "furniture repair": "Carpentry"
        }

        # Check special mappings first
        if input_text in special_mappings:
            target_name = special_mappings[input_text]
            for category in self.categories_cache:
                if category["name"] == target_name:
                    return category

        for category in self.categories_cache:
            category_name_lower = category["name"].lower()

            # Only exact match - no word-level matching to avoid false positives
            # This prevents "kitchen cleaning" from matching "Home Cleaning"
            if input_text == category_name_lower:
                return category

        return None

    async def _fuzzy_match(self, input_text: str) -> List[Dict[str, Any]]:
        """Fuzzy string matching with confidence scores"""
        from difflib import SequenceMatcher

        results = []
        if not self.categories_cache:
            return results

        for category in self.categories_cache:
            category_name_lower = category["name"].lower()

            # Calculate similarity ratio
            similarity = SequenceMatcher(None, input_text, category_name_lower).ratio()

            # Higher threshold to prevent false matches like "car care" -> "carpentry"
            if similarity >= 0.75:  # Increased threshold from 0.6 to 0.75
                # Additional check: ensure significant character overlap
                input_chars = set(input_text.replace(" ", ""))
                category_chars = set(category_name_lower.replace(" ", ""))
                char_overlap = len(input_chars.intersection(category_chars)) / max(len(input_chars), len(category_chars))

                if char_overlap >= 0.6:  # Require 60% character overlap
                    results.append({
                        "category": category,
                        "confidence": min(0.9, similarity * char_overlap),  # Adjust confidence based on overlap
                        "method": "fuzzy",
                        "original_input": input_text
                    })

        return results

    async def _semantic_match(self, input_text: str) -> List[Dict[str, Any]]:
        """Semantic similarity matching using sentence transformers"""
        if not self.semantic_model or not self.categories_cache:
            return []

        try:
            # Skip semantic matching for very short inputs (like "AC") to avoid false matches
            if len(input_text.strip()) <= 2:
                return []

            # Get embeddings
            input_embedding = self.semantic_model.encode([input_text])
            category_names = [cat["name"] for cat in self.categories_cache]
            category_embeddings = self.semantic_model.encode(category_names)

            # Calculate similarities
            similarities = cosine_similarity(input_embedding, category_embeddings)[0]

            results = []
            for i, similarity in enumerate(similarities):
                # Higher threshold for semantic matching to reduce false positives
                if similarity >= 0.65:  # Increased from 0.5 to 0.65
                    results.append({
                        "category": self.categories_cache[i],
                        "confidence": min(0.85, float(similarity)),  # Cap at 0.85 for semantic matches
                        "method": "semantic",
                        "original_input": input_text
                    })

            return results

        except Exception as e:
            logger.error(f"Semantic matching failed: {e}")
            return []


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
        Initialize ServiceAgent with NLP capabilities

        Args:
            db: Database session
        """
        self.db = db
        self.category_service = CategoryService(db)
        self.response_generator = ResponseGenerator()
        self.category_matcher = CategoryMatcher(db)
        logger.info("ServiceAgent initialized with NLP capabilities")
    
    async def execute(
        self,
        intent: str,
        entities: Dict[str, Any],
        user: User,
        session_id: str,
        message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Main execution method - routes to appropriate handler based on action

        Args:
            intent: Intent type (should be "service_inquiry" or "service_information")
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
            message: Original user message (optional, used for smart inference)

        Returns:
            Response dict with service information
        """
        logger.info(f"ServiceAgent.execute called: intent={intent}, action={entities.get('action')}, user_id={user.id}, message='{message[:50] if message else None}...'")

        try:
            # If no action provided and we have the original message, infer action and query
            if "action" not in entities and message:
                logger.info(f"[ServiceAgent] No action in entities, inferring from message: '{message}'")
                entities = await self._infer_action_and_query(message, entities)
                logger.info(f"[ServiceAgent] Inferred entities: {entities}")

            # Get action from entities
            action = entities.get("action", "browse_categories")
            
            # Route to appropriate method
            if action == "browse_categories":
                return await self._browse_categories(entities, user)
            elif action == "browse_subcategories":
                return await self._browse_subcategories(entities, user)
            elif action == "browse_subcategories_by_category":
                return await self._browse_subcategories_by_category(entities, user, message)
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
            
            # Generate natural response using ResponseGenerator
            services_data = [
                {
                    "name": rc.name,
                    "price": float(rc.price),
                    "strike_price": float(rc.strike_price) if rc.strike_price else None
                }
                for rc in rate_cards
            ]

            response_text = await self.response_generator.generate_service_list_response(
                services=services_data,
                conversation_history=None,  # TODO: Pass conversation history from coordinator
                user_name=getattr(user, 'first_name', None)
            )

            return {
                "response": response_text,
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
                price_value = getattr(rc, 'price', 0)
                strike_price_value = getattr(rc, 'strike_price', None)

                price_text = f"₹{float(price_value):,.2f}"
                if strike_price_value is not None:
                    price_text = f"₹{float(price_value):,.2f} (was ₹{float(strike_price_value):,.2f})"
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
                            "price": float(getattr(rc, 'price', 0)),
                            "strike_price": float(getattr(rc, 'strike_price', 0)) if getattr(rc, 'strike_price', None) is not None else None
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
                price_value = getattr(rc, 'price', 0)
                strike_price_value = getattr(rc, 'strike_price', None)

                price_text = f"₹{float(price_value):,.2f}"
                if strike_price_value is not None:
                    price_text = f"₹{float(price_value):,.2f} (was ₹{float(strike_price_value):,.2f})"
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
                            "price": float(getattr(rc, 'price', 0)),
                            "strike_price": float(getattr(rc, 'strike_price', 0)) if getattr(rc, 'strike_price', None) is not None else None
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

    async def _infer_action_and_query(self, message: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """
        NLP-Enhanced action and query inference with subcategory detection

        Detects:
        - Subcategory queries: "subcategories for X", "what X services", "show me X options"
        - Regular search queries: "find X", "search for X"
        - Category browsing: "show categories", "what categories"

        Args:
            message: Original user message
            entities: Existing entities dict (may be empty)

        Returns:
            Updated entities dict with inferred action and query
        """
        message_lower = message.lower().strip()
        updated_entities = entities.copy()

        # Priority 1: Subcategory queries - NEW NLP-ENHANCED DETECTION
        subcategory_patterns = [
            # Pattern 1: "subcategories for [service]" - capture everything after "for" until end or specific words
            r'\b(subcategories|sub-categories)\s+for\s+(?P<service>(?:[\w\s]+?)(?=\s*$|[.!?]))',
            # Pattern 2: "what [service] services do you have"
            r'\bwhat\s+(?P<service>[\w\s]+?)\s+(services?|options?)\s+do\s+you\s+have',
            # Pattern 3: "show me [service] options/subcategories"
            r'\bshow\s+me\s+(?P<service>[\w\s]+?)\s+(services?|options?|subcategories)',
            # Pattern 4: "[service] subcategories"
            r'\b(?P<service>[\w\s]+?)\s+(subcategories|sub-categories)',
            # Pattern 5: "types of [service] services"
            r'\btypes?\s+of\s+(?P<service>[\w\s]+?)\s+services?',
            # Pattern 6: "list [service] services/options"
            r'\blist\s+(?P<service>[\w\s]+?)\s+(services?|options?)',
        ]

        for pattern in subcategory_patterns:
            match = re.search(pattern, message_lower)
            if match:
                service_keyword = match.group('service').strip()
                # Clean up common words
                service_keyword = re.sub(r'\b(the|a|an|some|any|all)\b', '', service_keyword).strip()

                if service_keyword:
                    updated_entities["action"] = "browse_subcategories_by_category"
                    updated_entities["service_keyword"] = service_keyword
                    logger.info(f"[_infer_action_and_query] Detected subcategory query: service='{service_keyword}'")
                    return updated_entities

        # Priority 2: Category browsing - Enhanced patterns
        category_patterns = [
            r'\b(what|which|show|list|display)\s+(service\s+)?(categories|types)',
            r'\bshow\s+me\s+all\s+service\s+categories',
            r'\blist\s+all\s+categories',
            r'\ball\s+service\s+categories',
            r'\bwhat\s+categories\s+do\s+you\s+have',
            r'\bservice\s+categories'
        ]

        for pattern in category_patterns:
            if re.search(pattern, message_lower):
                updated_entities["action"] = "browse_categories"
                logger.info(f"[_infer_action_and_query] Matched category pattern: {pattern}")
                return updated_entities

        # Priority 3: Service search patterns (including conversational prefixes)
        search_patterns = [
            # "ok details on X", "details on X", "tell me about X"
            r'(?:ok\s+)?(?:details?|info|information)\s+(?:on|about|for)\s+(?P<query>[\w\s]+?)(?:\s*$|[.!?])',
            # "show/tell/give me about X services"
            r'\b(show|tell|give)\s+(me\s+)?(about\s+)?(?P<query>[\w\s]+?)\s+(services?|repair|maintenance)',
            # "search/find/look for X"
            r'\b(search|find|look\s+for)\s+(?P<query>[\w\s]+)',
            # "do you have X services"
            r'\b(do\s+you\s+have|have\s+you\s+got)\s+(?P<query>[\w\s]+?)\s+(services?|repair)',
            # "i want to book X" - extract service name for search
            r'\b(?:i\s+)?(?:want\s+to|wanna|would\s+like\s+to)\s+(?:book|get|schedule)\s+(?P<query>[\w\s]+?)(?:\s*$|[.!?])',
        ]

        for pattern in search_patterns:
            match = re.search(pattern, message_lower)
            if match:
                query = match.group('query').strip()
                # Clean up common words and filler words
                query = re.sub(r'\b(the|a|an|some|any|ok|okay|please)\b', '', query).strip()
                if query:
                    updated_entities["action"] = "search"
                    updated_entities["query"] = query
                    logger.info(f"[_infer_action_and_query] Matched search pattern: query='{query}'")
                    return updated_entities

        # Priority 4: Check if message matches a category name (for browsing subcategories)
        # This handles cases like "home cleaning", "plumbing", "electrical" without trigger words
        # IMPORTANT: Only match if message is short (1-3 words) and exact/high confidence match
        # This prevents intercepting booking flow follow-ups
        word_count = len(message_lower.split())
        if 1 <= word_count <= 3:
            try:
                match_result = await self.category_matcher.match_category(message_lower)
                # Only use exact matches (confidence = 1.0) to avoid false positives
                # This ensures we only match actual category names, not subcategories
                if match_result and match_result["confidence"] == 1.0 and match_result["method"] == "exact":
                    # Exact category name match
                    updated_entities["action"] = "browse_subcategories_by_category"
                    updated_entities["service_keyword"] = message_lower
                    logger.info(f"[_infer_action_and_query] Matched category name: '{message_lower}' (confidence: {match_result['confidence']})")
                    return updated_entities
            except Exception as e:
                logger.warning(f"[_infer_action_and_query] Category matching failed: {e}")

        # Priority 5: Single word service detection (for search, not subcategories)
        # This is for queries like just "repair" or "installation" that don't match categories
        single_word_match = re.search(r'^\s*(\w+)\s*$', message_lower)
        if single_word_match:
            word = single_word_match.group(1)
            # Check if it's a potential service keyword
            if len(word) >= 3:  # Avoid very short words
                updated_entities["action"] = "search"
                updated_entities["query"] = word
                logger.info(f"[_infer_action_and_query] Single word service search: query='{word}'")
                return updated_entities

        # Default fallbacks
        if 'service' in message_lower or 'category' in message_lower:
            updated_entities["action"] = "browse_categories"
            logger.info(f"[_infer_action_and_query] Default to browse_categories (mentions 'service')")
        else:
            # Last resort: search with entire message as query
            updated_entities["action"] = "search"
            updated_entities["query"] = message_lower
            logger.info(f"[_infer_action_and_query] Last resort: search with full message as query")

        return updated_entities

    async def _browse_subcategories_by_category(self, entities: Dict[str, Any], user: User, message: Optional[str]) -> Dict[str, Any]:
        """
        NLP-Enhanced subcategory browsing by category name/keyword

        Uses CategoryMatcher to intelligently map user keywords to categories
        with confidence-based responses.

        Args:
            entities: Must contain service_keyword
            user: Current user
            message: Original message for context

        Returns:
            Response dict with subcategories or clarification questions
        """
        try:
            service_keyword = entities.get("service_keyword")
            if not service_keyword:
                return {
                    "response": "I need to know which service category you're interested in. Could you specify the service type?",
                    "action_taken": "missing_entity",
                    "metadata": {"missing": "service_keyword"}
                }

            logger.info(f"Processing subcategory query for keyword: '{service_keyword}'")

            # Use NLP to match category
            match_result = await self.category_matcher.match_category(service_keyword)

            if not match_result:
                return await self._handle_no_category_match(service_keyword)

            confidence = match_result["confidence"]
            category = match_result["category"]
            method = match_result["method"]

            logger.info(f"Category match: {category['name']} (confidence: {confidence}, method: {method})")

            # Handle response based on confidence level
            if confidence >= 0.8:
                # High confidence - return subcategories directly
                return await self._get_subcategories_response(category, match_result)
            elif confidence >= 0.5:
                # Medium confidence - ask for confirmation
                return await self._ask_category_confirmation(category, service_keyword, confidence, method)
            else:
                # Low confidence - suggest alternatives
                return await self._suggest_category_alternatives(service_keyword)

        except Exception as e:
            logger.error(f"Error in _browse_subcategories_by_category: {str(e)}", exc_info=True)
            return {
                "response": f"❌ Sorry, I encountered an error while finding subcategories. Please try again.",
                "action_taken": "error",
                "metadata": {"error": str(e)}
            }

    async def _get_subcategories_response(self, category: Dict, match_result: Dict) -> Dict[str, Any]:
        """Get subcategories for a category and format response"""
        try:
            category_id = category["id"]
            category_name = category["name"]

            # Get subcategories from database
            query = select(Subcategory).where(
                and_(
                    Subcategory.category_id == category_id,
                    Subcategory.is_active == True
                )
            ).order_by(Subcategory.name)

            result = await self.db.execute(query)
            subcategories = result.scalars().all()

            if not subcategories:
                return {
                    "response": f"No subcategories found for {category_name}. This category might not have specific service types available.",
                    "action_taken": "no_subcategories",
                    "metadata": {
                        "category": category,
                        "match_result": match_result
                    }
                }

            # Format response
            response_lines = []

            # Add context about the match if it was corrected or inferred
            method = match_result.get("method", "exact")
            if method == "spell_corrected":
                corrected_to = match_result.get("corrected_to", "")
                response_lines.append(f"I found {category_name} services (corrected from '{match_result['original_input']}' to '{corrected_to}').\n")
            elif method in ["fuzzy", "semantic"] and match_result["confidence"] < 0.9:
                response_lines.append(f"I found {category_name} services for your query.\n")
            else:
                response_lines.append(f"{category_name} subcategories:\n")

            # Add subcategories list
            for idx, subcat in enumerate(subcategories, 1):
                response_lines.append(f"{idx}. {subcat.name}")

            response_lines.append(f"\nWould you like details on any subcategory?")

            return {
                "response": "\n".join(response_lines),
                "action_taken": "subcategories_listed",
                "metadata": {
                    "category": category,
                    "subcategories": [
                        {
                            "id": subcat.id,
                            "name": subcat.name,
                            "description": subcat.description
                        }
                        for subcat in subcategories
                    ],
                    "match_result": match_result
                }
            }

        except Exception as e:
            logger.error(f"Error getting subcategories response: {str(e)}")
            return {
                "response": f"❌ Failed to load subcategories: {str(e)}",
                "action_taken": "error",
                "metadata": {"error": str(e)}
            }

    async def _ask_category_confirmation(self, category: Dict, original_input: str, confidence: float, method: str) -> Dict[str, Any]:
        """Ask user to confirm category when confidence is medium"""
        category_name = category["name"]

        response_lines = [
            f"Did you mean '{category_name}' services? (confidence: {confidence:.0%})"
        ]

        if method == "spell_corrected":
            response_lines.append(f"I corrected '{original_input}' to find this match.")
        elif method == "semantic":
            response_lines.append(f"I found this category related to '{original_input}'.")

        response_lines.extend([
            f"\nReply 'yes' to see {category_name} subcategories, or specify a different service type."
        ])

        return {
            "response": "\n".join(response_lines),
            "action_taken": "confirmation_requested",
            "metadata": {
                "category": category,
                "original_input": original_input,
                "confidence": confidence,
                "method": method
            }
        }

    async def _suggest_category_alternatives(self, service_keyword: str) -> Dict[str, Any]:
        """Suggest multiple category options when confidence is low"""
        try:
            # Get all categories for suggestions
            query = select(Category).where(Category.is_active == True).order_by(Category.name)
            result = await self.db.execute(query)
            categories = result.scalars().all()

            response_lines = [
                f"I couldn't find a clear match for '{service_keyword}'. Here are our available service categories:\n"
            ]

            for idx, cat in enumerate(categories[:10], 1):  # Limit to first 10
                response_lines.append(f"{idx}. {cat.name}")

            response_lines.append(f"\nWhich category are you interested in?")

            return {
                "response": "\n".join(response_lines),
                "action_taken": "alternatives_suggested",
                "metadata": {
                    "original_input": service_keyword,
                    "suggested_categories": [
                        {"id": cat.id, "name": cat.name}
                        for cat in categories[:10]
                    ]
                }
            }

        except Exception as e:
            logger.error(f"Error suggesting alternatives: {str(e)}")
            return {
                "response": f"I couldn't find a match for '{service_keyword}'. Please try a different service type or browse our categories.",
                "action_taken": "error",
                "metadata": {"error": str(e)}
            }

    async def _handle_no_category_match(self, service_keyword: str) -> Dict[str, Any]:
        """Handle cases where no category matches at all"""
        return {
            "response": f"I couldn't find any services matching '{service_keyword}'. "
                       f"Try a different search term or ask to see all categories.",
            "action_taken": "no_match",
            "metadata": {"original_input": service_keyword}
        }


# Export
__all__ = ["ServiceAgent"]


