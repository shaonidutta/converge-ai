"""
Application Configuration

Centralized configuration management using Pydantic Settings.
Loads configuration from environment variables and .env file.
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field, validator


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    
    All settings can be overridden via environment variables or .env file
    """
    
    # ============================================
    # Application Settings
    # ============================================
    APP_NAME: str = "ConvergeAI"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=True)
    
    # ============================================
    # Database Settings
    # ============================================
    DB_HOST: str = Field(default="localhost", env="DB_HOST")
    DB_PORT: int = Field(default=3306, env="DB_PORT")
    DB_USER: str = Field(default="root", env="DB_USER")
    DB_PASSWORD: str = Field(default="", env="DB_PASSWORD")
    DB_NAME: str = Field(default="convergeai", env="DB_NAME")
    
    @property
    def DATABASE_URL(self) -> str:
        """Construct async database URL"""
        return f"mysql+aiomysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    # ============================================
    # Redis Settings
    # ============================================
    REDIS_HOST: str = Field(default="localhost", env="REDIS_HOST")
    REDIS_PORT: int = Field(default=6379, env="REDIS_PORT")
    REDIS_PASSWORD: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    REDIS_DB: int = Field(default=0, env="REDIS_DB")
    
    # ============================================
    # Security Settings
    # ============================================
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    
    # CORS
    ALLOWED_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:3001",
        env="ALLOWED_ORIGINS"
    )
    
    @property
    def ALLOWED_ORIGINS_LIST(self) -> List[str]:
        """Parse ALLOWED_ORIGINS into list"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    # ============================================
    # Gemini LLM Settings
    # ============================================
    GEMINI_API_KEY: str = Field(..., env="GEMINI_API_KEY")
    GEMINI_MODEL: str = Field(default="gemini-2.0-flash", env="GEMINI_MODEL")  # Updated to Gemini 2.0 Flash (1.5 deprecated)
    GEMINI_TEMPERATURE: float = Field(default=0.7, env="GEMINI_TEMPERATURE")
    GEMINI_MAX_TOKENS: int = Field(default=1024, env="GEMINI_MAX_TOKENS")
    GEMINI_TOP_P: float = Field(default=0.95, env="GEMINI_TOP_P")
    GEMINI_TOP_K: int = Field(default=40, env="GEMINI_TOP_K")
    
    # ============================================
    # Pinecone Vector Database Settings
    # ============================================
    PINECONE_API_KEY: Optional[str] = Field(default=None, env="PINECONE_API_KEY")
    PINECONE_ENVIRONMENT: Optional[str] = Field(default="us-east-1", env="PINECONE_ENVIRONMENT")
    PINECONE_INDEX_NAME: Optional[str] = Field(default="convergeai-docs", env="PINECONE_INDEX_NAME")
    
    # ============================================
    # Conversation Settings
    # ============================================
    CONVERSATION_HISTORY_LIMIT: int = Field(default=10, env="CONVERSATION_HISTORY_LIMIT")
    MAX_RETRY_ATTEMPTS: int = Field(default=3, env="MAX_RETRY_ATTEMPTS")
    DIALOG_STATE_EXPIRY_HOURS: int = Field(default=24, env="DIALOG_STATE_EXPIRY_HOURS")
    
    # ============================================
    # Logging Settings
    # ============================================
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT"
    )
    
    # ============================================
    # Rate Limiting Settings
    # ============================================
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    RATE_LIMIT_PER_HOUR: int = Field(default=1000, env="RATE_LIMIT_PER_HOUR")
    
    # ============================================
    # Feature Flags
    # ============================================
    ENABLE_SLOT_FILLING: bool = Field(default=True, env="ENABLE_SLOT_FILLING")
    ENABLE_AGENT_EXECUTION: bool = Field(default=False, env="ENABLE_AGENT_EXECUTION")
    ENABLE_RAG_PIPELINE: bool = Field(default=False, env="ENABLE_RAG_PIPELINE")
    
    class Config:
        """Pydantic config"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "allow"  # Allow extra fields from .env


# ============================================
# Global Settings Instance
# ============================================
settings = Settings()


# ============================================
# Helper Functions
# ============================================
def get_settings() -> Settings:
    """
    Get application settings instance
    
    Returns:
        Settings instance
    """
    return settings


def is_production() -> bool:
    """Check if running in production environment"""
    return settings.ENVIRONMENT.lower() == "production"


def is_development() -> bool:
    """Check if running in development environment"""
    return settings.ENVIRONMENT.lower() == "development"


def is_testing() -> bool:
    """Check if running in testing environment"""
    return settings.ENVIRONMENT.lower() == "testing"

