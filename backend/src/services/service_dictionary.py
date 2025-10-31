"""
Service Dictionary - Database-backed dictionary for spell correction

This service maintains a cached dictionary of all service names from the database
for fast spell correction and fuzzy matching.

Features:
- Loads all RateCard names, Subcategory names, and Category names
- Builds a spell-checker dictionary
- Provides fuzzy matching with confidence scores
- Auto-refreshes cache periodically
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
import re

# NLP imports
try:
    from spellchecker import SpellChecker
    from difflib import SequenceMatcher
    NLP_AVAILABLE = True
except ImportError:
    NLP_AVAILABLE = False
    logging.warning("SpellChecker not available. Install pyspellchecker for spell correction.")

from src.core.models import RateCard, Subcategory, Category

logger = logging.getLogger(__name__)


class ServiceDictionary:
    """
    Database-backed dictionary for service name spell correction
    
    Maintains a cached dictionary of all service names and provides
    spell correction and fuzzy matching capabilities.
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize ServiceDictionary
        
        Args:
            db: Database session
        """
        self.db = db
        self.spell_checker = SpellChecker() if NLP_AVAILABLE else None
        
        # Cache
        self.service_names: List[str] = []
        self.service_metadata: Dict[str, Dict[str, Any]] = {}
        self.cache_timestamp: Optional[datetime] = None
        self.cache_ttl = timedelta(hours=1)  # Refresh cache every hour
        
    async def refresh_cache(self, force: bool = False) -> None:
        """
        Refresh the service dictionary cache from database
        
        Args:
            force: Force refresh even if cache is still valid
        """
        # Check if cache is still valid
        if not force and self.cache_timestamp:
            if datetime.now() - self.cache_timestamp < self.cache_ttl:
                logger.debug("[ServiceDictionary] Cache still valid, skipping refresh")
                return
        
        logger.info("[ServiceDictionary] Refreshing service dictionary cache...")
        
        try:
            # Load all RateCards
            rate_cards_query = select(RateCard).where(RateCard.is_active == True)
            rate_cards_result = await self.db.execute(rate_cards_query)
            rate_cards = rate_cards_result.scalars().all()
            
            # Load all Subcategories
            subcategories_query = select(Subcategory).where(Subcategory.is_active == True)
            subcategories_result = await self.db.execute(subcategories_query)
            subcategories = subcategories_result.scalars().all()
            
            # Load all Categories
            categories_query = select(Category).where(Category.is_active == True)
            categories_result = await self.db.execute(categories_query)
            categories = categories_result.scalars().all()
            
            # Build dictionary
            self.service_names = []
            self.service_metadata = {}
            
            # Add RateCards
            for rc in rate_cards:
                name_lower = rc.name.lower()
                self.service_names.append(name_lower)
                self.service_metadata[name_lower] = {
                    "type": "rate_card",
                    "id": rc.id,
                    "name": rc.name,
                    "category_id": rc.category_id,
                    "subcategory_id": rc.subcategory_id,
                    "price": float(rc.price) if rc.price else None
                }
            
            # Add Subcategories
            for sub in subcategories:
                name_lower = sub.name.lower()
                if name_lower not in self.service_metadata:
                    self.service_names.append(name_lower)
                self.service_metadata[name_lower] = {
                    "type": "subcategory",
                    "id": sub.id,
                    "name": sub.name,
                    "category_id": sub.category_id,
                    "subcategory_id": sub.id
                }
            
            # Add Categories
            for cat in categories:
                name_lower = cat.name.lower()
                if name_lower not in self.service_metadata:
                    self.service_names.append(name_lower)
                self.service_metadata[name_lower] = {
                    "type": "category",
                    "id": cat.id,
                    "name": cat.name,
                    "category_id": cat.id,
                    "subcategory_id": None
                }
            
            # Update spell checker dictionary
            if self.spell_checker:
                self.spell_checker.word_frequency.load_words(self.service_names)
            
            self.cache_timestamp = datetime.now()
            logger.info(f"[ServiceDictionary] Cache refreshed: {len(self.service_names)} service names loaded")
            
        except Exception as e:
            logger.error(f"[ServiceDictionary] Failed to refresh cache: {e}")
            raise
    
    async def correct_spelling(self, text: str) -> Tuple[str, float]:
        """
        Correct spelling of service name
        
        Args:
            text: Input text (possibly with typos)
        
        Returns:
            Tuple of (corrected_text, confidence)
            confidence: 1.0 if no correction needed, 0.8 if corrected
        """
        await self.refresh_cache()
        
        if not self.spell_checker:
            return text, 1.0
        
        text_lower = text.lower().strip()
        
        # Check if exact match exists
        if text_lower in self.service_names:
            return text_lower, 1.0
        
        # Try spell correction on individual words
        words = text_lower.split()
        corrected_words = []
        was_corrected = False
        
        for word in words:
            if word in self.service_names:
                corrected_words.append(word)
            else:
                # Try to correct this word
                corrected = self.spell_checker.correction(word)
                if corrected and corrected != word:
                    corrected_words.append(corrected)
                    was_corrected = True
                else:
                    corrected_words.append(word)
        
        corrected_text = " ".join(corrected_words)
        confidence = 0.8 if was_corrected else 1.0
        
        return corrected_text, confidence
    
    async def fuzzy_match(self, query: str, threshold: float = 0.6) -> List[Dict[str, Any]]:
        """
        Find fuzzy matches for a query string
        
        Args:
            query: Search query
            threshold: Minimum similarity score (0.0 to 1.0)
        
        Returns:
            List of matches with metadata and confidence scores
            [
                {
                    "name": "texture painting - basic",
                    "confidence": 0.85,
                    "metadata": {...}
                },
                ...
            ]
        """
        await self.refresh_cache()
        
        query_lower = query.lower().strip()
        matches = []
        
        for service_name in self.service_names:
            # Calculate similarity
            similarity = SequenceMatcher(None, query_lower, service_name).ratio()
            
            if similarity >= threshold:
                matches.append({
                    "name": service_name,
                    "confidence": similarity,
                    "metadata": self.service_metadata[service_name]
                })
        
        # Sort by confidence (descending)
        matches.sort(key=lambda x: x["confidence"], reverse=True)
        
        return matches
    
    async def search(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for services matching query (with spell correction and fuzzy matching)
        
        Args:
            query: Search query (e.g., "texture pianting")
        
        Returns:
            List of matching services with metadata
        """
        await self.refresh_cache()
        
        # Step 1: Try exact match
        query_lower = query.lower().strip()
        if query_lower in self.service_metadata:
            return [{
                "name": query_lower,
                "confidence": 1.0,
                "method": "exact",
                "metadata": self.service_metadata[query_lower]
            }]
        
        # Step 2: Try spell correction
        corrected, correction_confidence = await self.correct_spelling(query)
        if corrected != query_lower and corrected in self.service_metadata:
            return [{
                "name": corrected,
                "confidence": correction_confidence,
                "method": "spell_corrected",
                "original_query": query,
                "metadata": self.service_metadata[corrected]
            }]
        
        # Step 3: Try fuzzy matching
        fuzzy_matches = await self.fuzzy_match(query, threshold=0.6)
        if fuzzy_matches:
            return [{
                "name": match["name"],
                "confidence": match["confidence"],
                "method": "fuzzy",
                "original_query": query,
                "metadata": match["metadata"]
            } for match in fuzzy_matches[:5]]  # Return top 5 matches
        
        return []

