"""
Service Name Resolver - Resolves user-provided service names to database entities

This service handles the complex task of mapping user input (which could be:
- A category name: "painting"
- A subcategory name: "texture painting"
- A specific service name: "texture painting - basic"
- A typo: "texture pianting"
- A partial match: "texture"

To the correct database entities (Category, Subcategory, RateCard) with metadata.

This is the KEY component that solves Issues 2, 3, 4, and 5 from the conversation analysis.
"""

import logging
from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
import re

from src.core.models import RateCard, Subcategory, Category
from src.services.service_dictionary import ServiceDictionary

logger = logging.getLogger(__name__)


class ServiceResolutionResult:
    """
    Result of service name resolution
    
    Contains all metadata needed for booking flow
    """
    def __init__(
        self,
        resolved: bool,
        confidence: float,
        method: str,
        original_query: str,
        corrected_query: Optional[str] = None,
        rate_card_id: Optional[int] = None,
        category_id: Optional[int] = None,
        subcategory_id: Optional[int] = None,
        service_name: Optional[str] = None,
        category_name: Optional[str] = None,
        subcategory_name: Optional[str] = None,
        price: Optional[float] = None,
        multiple_matches: Optional[List[Dict[str, Any]]] = None,
        error_message: Optional[str] = None
    ):
        self.resolved = resolved
        self.confidence = confidence
        self.method = method
        self.original_query = original_query
        self.corrected_query = corrected_query
        self.rate_card_id = rate_card_id
        self.category_id = category_id
        self.subcategory_id = subcategory_id
        self.service_name = service_name
        self.category_name = category_name
        self.subcategory_name = subcategory_name
        self.price = price
        self.multiple_matches = multiple_matches or []
        self.error_message = error_message
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for easy serialization"""
        return {
            "resolved": self.resolved,
            "confidence": self.confidence,
            "method": self.method,
            "original_query": self.original_query,
            "corrected_query": self.corrected_query,
            "rate_card_id": self.rate_card_id,
            "category_id": self.category_id,
            "subcategory_id": self.subcategory_id,
            "service_name": self.service_name,
            "category_name": self.category_name,
            "subcategory_name": self.subcategory_name,
            "price": self.price,
            "multiple_matches": self.multiple_matches,
            "error_message": self.error_message
        }


class ServiceNameResolver:
    """
    Resolves user-provided service names to database entities
    
    This is the core component that enables users to say:
    - "i want to book texture painting" (specific service)
    - "book texture pianting" (with typo)
    - "details on texture painting" (after seeing it in search)
    
    And have the system correctly resolve it to the right RateCard/Subcategory/Category.
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize ServiceNameResolver
        
        Args:
            db: Database session
        """
        self.db = db
        self.dictionary = ServiceDictionary(db)
    
    async def resolve(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> ServiceResolutionResult:
        """
        Resolve a service name query to database entities
        
        Args:
            query: User's service name query (e.g., "texture pianting")
            context: Optional context (recently mentioned services, conversation history)
        
        Returns:
            ServiceResolutionResult with resolved metadata
        """
        logger.info(f"[ServiceNameResolver] Resolving query: '{query}'")
        
        if not query or not query.strip():
            return ServiceResolutionResult(
                resolved=False,
                confidence=0.0,
                method="error",
                original_query=query,
                error_message="Empty query"
            )
        
        query = query.strip()
        
        # Step 1: Check context for recently mentioned services
        if context:
            context_result = await self._check_context(query, context)
            if context_result:
                return context_result
        
        # Step 2: Try dictionary-based search (with spell correction)
        dictionary_matches = await self.dictionary.search(query)
        
        if not dictionary_matches:
            return ServiceResolutionResult(
                resolved=False,
                confidence=0.0,
                method="no_match",
                original_query=query,
                error_message=f"No services found matching '{query}'"
            )
        
        # Step 3: If single high-confidence match, resolve it
        if len(dictionary_matches) == 1 or dictionary_matches[0]["confidence"] >= 0.9:
            best_match = dictionary_matches[0]
            return await self._resolve_match(best_match, query)
        
        # Step 4: Multiple matches - return them for user clarification
        return ServiceResolutionResult(
            resolved=False,
            confidence=dictionary_matches[0]["confidence"],
            method="multiple_matches",
            original_query=query,
            multiple_matches=[
                {
                    "name": match["name"],
                    "confidence": match["confidence"],
                    "metadata": match["metadata"]
                }
                for match in dictionary_matches[:5]
            ],
            error_message=f"Found {len(dictionary_matches)} services matching '{query}'. Please be more specific."
        )
    
    async def _check_context(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> Optional[ServiceResolutionResult]:
        """
        Check if query refers to a recently mentioned service in context
        
        Args:
            query: User query
            context: Conversation context
        
        Returns:
            ServiceResolutionResult if context match found, None otherwise
        """
        # Check for recently mentioned services in context
        recent_services = context.get("recent_services", [])
        
        if not recent_services:
            return None
        
        # Check if query is a reference like "that one", "the first one", "texture painting"
        query_lower = query.lower()
        
        for service in recent_services:
            service_name = service.get("name", "").lower()
            if query_lower in service_name or service_name in query_lower:
                # Found a context match
                logger.info(f"[ServiceNameResolver] Context match: '{query}' → '{service_name}'")
                return await self._resolve_from_metadata(service, query, method="context")
        
        return None
    
    async def _resolve_match(
        self,
        match: Dict[str, Any],
        original_query: str
    ) -> ServiceResolutionResult:
        """
        Resolve a dictionary match to full service metadata
        
        Args:
            match: Match from ServiceDictionary
            original_query: Original user query
        
        Returns:
            ServiceResolutionResult with full metadata
        """
        metadata = match["metadata"]
        match_type = metadata["type"]
        
        if match_type == "rate_card":
            # Direct RateCard match - best case
            return ServiceResolutionResult(
                resolved=True,
                confidence=match["confidence"],
                method=match.get("method", "exact"),
                original_query=original_query,
                corrected_query=match["name"] if match.get("method") == "spell_corrected" else None,
                rate_card_id=metadata["id"],
                category_id=metadata["category_id"],
                subcategory_id=metadata["subcategory_id"],
                service_name=metadata["name"],
                price=metadata.get("price")
            )
        
        elif match_type == "subcategory":
            # Subcategory match - need to find a default RateCard
            # For now, return subcategory info and let booking flow handle it
            return ServiceResolutionResult(
                resolved=True,
                confidence=match["confidence"],
                method=match.get("method", "exact"),
                original_query=original_query,
                corrected_query=match["name"] if match.get("method") == "spell_corrected" else None,
                category_id=metadata["category_id"],
                subcategory_id=metadata["subcategory_id"],
                subcategory_name=metadata["name"]
            )
        
        elif match_type == "category":
            # Category match - need subcategory selection
            return ServiceResolutionResult(
                resolved=True,
                confidence=match["confidence"],
                method=match.get("method", "exact"),
                original_query=original_query,
                corrected_query=match["name"] if match.get("method") == "spell_corrected" else None,
                category_id=metadata["id"],
                category_name=metadata["name"]
            )
        
        return ServiceResolutionResult(
            resolved=False,
            confidence=0.0,
            method="error",
            original_query=original_query,
            error_message=f"Unknown match type: {match_type}"
        )
    
    async def _resolve_from_metadata(
        self,
        metadata: Dict[str, Any],
        original_query: str,
        method: str = "context"
    ) -> ServiceResolutionResult:
        """
        Resolve service from metadata (e.g., from context)
        
        Args:
            metadata: Service metadata
            original_query: Original user query
            method: Resolution method
        
        Returns:
            ServiceResolutionResult
        """
        return ServiceResolutionResult(
            resolved=True,
            confidence=0.95,
            method=method,
            original_query=original_query,
            rate_card_id=metadata.get("rate_card_id"),
            category_id=metadata.get("category_id"),
            subcategory_id=metadata.get("subcategory_id"),
            service_name=metadata.get("name"),
            price=metadata.get("price")
        )

