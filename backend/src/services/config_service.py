"""
Configuration Service for runtime feature flags and settings
"""

import logging
from typing import Any, Optional, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.core.models import OpsConfig


class ConfigService:
    """
    Service for managing runtime configuration
    
    Provides feature flags and configurable settings that can be
    changed without code deployment.
    
    Features:
    - In-memory caching for performance
    - Default values for missing configs
    - Type conversion support
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize config service
        
        Args:
            db: Async database session
        """
        self.db = db
        self.logger = logging.getLogger(__name__)
        self._cache: Dict[str, str] = {}  # In-memory cache
    
    async def get_config(
        self, 
        key: str, 
        default: Any = None,
        use_cache: bool = True
    ) -> Any:
        """
        Get configuration value by key
        
        Args:
            key: Configuration key
            default: Default value if key not found
            use_cache: Whether to use cached value
        
        Returns:
            Configuration value or default
        """
        try:
            # Check cache first
            if use_cache and key in self._cache:
                self.logger.debug(f"Config cache hit: {key}")
                return self._cache[key]
            
            # Query database
            result = await self.db.execute(
                select(OpsConfig).where(OpsConfig.config_key == key)
            )
            config = result.scalar_one_or_none()
            
            if config:
                value = config.config_value
                
                # Update cache
                self._cache[key] = value
                
                self.logger.debug(f"Config retrieved: {key} = {value}")
                return value
            else:
                self.logger.debug(f"Config not found: {key}, using default: {default}")
                return default
                
        except Exception as e:
            self.logger.error(f"Error retrieving config {key}: {e}", exc_info=True)
            return default
    
    async def get_config_int(
        self, 
        key: str, 
        default: int = 0,
        use_cache: bool = True
    ) -> int:
        """
        Get configuration value as integer
        
        Args:
            key: Configuration key
            default: Default integer value
            use_cache: Whether to use cached value
        
        Returns:
            Configuration value as integer
        """
        value = await self.get_config(key, str(default), use_cache)
        try:
            return int(value)
        except (ValueError, TypeError):
            self.logger.warning(
                f"Config {key} value '{value}' is not a valid integer, "
                f"using default: {default}"
            )
            return default
    
    async def get_config_bool(
        self, 
        key: str, 
        default: bool = False,
        use_cache: bool = True
    ) -> bool:
        """
        Get configuration value as boolean
        
        Args:
            key: Configuration key
            default: Default boolean value
            use_cache: Whether to use cached value
        
        Returns:
            Configuration value as boolean
        """
        value = await self.get_config(key, str(default), use_cache)
        
        # Handle various boolean representations
        if isinstance(value, bool):
            return value
        
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on')
        
        return bool(value)
    
    async def set_config(
        self, 
        key: str, 
        value: str,
        description: Optional[str] = None
    ) -> OpsConfig:
        """
        Set configuration value
        
        Args:
            key: Configuration key
            value: Configuration value (stored as string)
            description: Optional description
        
        Returns:
            OpsConfig instance
        """
        try:
            # Check if config exists
            result = await self.db.execute(
                select(OpsConfig).where(OpsConfig.config_key == key)
            )
            config = result.scalar_one_or_none()
            
            if config:
                # Update existing config
                config.config_value = value
                if description:
                    config.description = description
                
                self.logger.info(f"Updated config: {key} = {value}")
            else:
                # Create new config
                config = OpsConfig(
                    config_key=key,
                    config_value=value,
                    description=description
                )
                self.db.add(config)
                
                self.logger.info(f"Created config: {key} = {value}")
            
            await self.db.commit()
            await self.db.refresh(config)
            
            # Update cache
            self._cache[key] = value
            
            return config
            
        except Exception as e:
            self.logger.error(f"Error setting config {key}: {e}", exc_info=True)
            await self.db.rollback()
            raise
    
    async def delete_config(self, key: str) -> bool:
        """
        Delete configuration
        
        Args:
            key: Configuration key
        
        Returns:
            True if deleted, False if not found
        """
        try:
            result = await self.db.execute(
                select(OpsConfig).where(OpsConfig.config_key == key)
            )
            config = result.scalar_one_or_none()
            
            if config:
                await self.db.delete(config)
                await self.db.commit()
                
                # Remove from cache
                self._cache.pop(key, None)
                
                self.logger.info(f"Deleted config: {key}")
                return True
            else:
                self.logger.warning(f"Config not found for deletion: {key}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error deleting config {key}: {e}", exc_info=True)
            await self.db.rollback()
            raise
    
    def clear_cache(self):
        """Clear in-memory cache"""
        self._cache.clear()
        self.logger.info("Config cache cleared")
    
    async def get_all_configs(self) -> Dict[str, str]:
        """
        Get all configurations
        
        Returns:
            Dictionary of all config key-value pairs
        """
        try:
            result = await self.db.execute(select(OpsConfig))
            configs = result.scalars().all()
            
            config_dict = {
                config.config_key: config.config_value 
                for config in configs
            }
            
            self.logger.info(f"Retrieved {len(config_dict)} configurations")
            return config_dict
            
        except Exception as e:
            self.logger.error(f"Error retrieving all configs: {e}", exc_info=True)
            raise

