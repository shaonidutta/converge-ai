"""
Application settings and configuration management
Uses Pydantic Settings for environment variable validation
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator, model_validator
from typing import Optional, List
from functools import lru_cache
import os


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """
    
    # Application
    APP_NAME: str = "ConvergeAI"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default="development", description="Environment: development, staging, production")
    DEBUG: bool = Field(default=True, description="Debug mode")
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    API_HOST: str = Field(default="0.0.0.0", description="API host")
    API_PORT: int = Field(default=8000, description="API port")
    
    # Database (MySQL)
    DATABASE_URL: str = Field(..., description="MySQL database URL")
    DB_POOL_SIZE: int = Field(default=20, description="Database connection pool size")
    DB_MAX_OVERFLOW: int = Field(default=10, description="Max overflow connections")
    DB_POOL_TIMEOUT: int = Field(default=30, description="Pool timeout in seconds")
    DB_POOL_RECYCLE: int = Field(default=3600, description="Pool recycle time in seconds")
    DB_ECHO: bool = Field(default=False, description="Echo SQL queries")
    
    # Redis
    REDIS_HOST: str = Field(default="localhost", description="Redis host")
    REDIS_PORT: int = Field(default=6379, description="Redis port")
    REDIS_DB: int = Field(default=0, description="Redis database number")
    REDIS_PASSWORD: Optional[str] = Field(default=None, description="Redis password")
    REDIS_URL: Optional[str] = Field(default=None, description="Redis URL (overrides host/port)")
    REDIS_POOL_SIZE: int = Field(default=10, description="Redis connection pool size")
    REDIS_SOCKET_TIMEOUT: int = Field(default=5, description="Redis socket timeout")
    REDIS_SOCKET_CONNECT_TIMEOUT: int = Field(default=5, description="Redis connection timeout")
    
    # JWT Authentication
    JWT_SECRET_KEY: str = Field(..., description="JWT secret key for signing tokens")
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="Access token expiry in minutes")
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, description="Refresh token expiry in days")
    
    # CORS
    CORS_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:3001",
        description="Allowed CORS origins (comma-separated)"
    )
    CORS_ALLOW_CREDENTIALS: bool = Field(default=True, description="Allow credentials in CORS")
    CORS_ALLOW_METHODS: str = Field(default="*", description="Allowed HTTP methods (comma-separated)")
    CORS_ALLOW_HEADERS: str = Field(default="*", description="Allowed HTTP headers (comma-separated)")
    
    # Pinecone Vector Database (Serverless)
    PINECONE_API_KEY: str = Field(..., description="Pinecone API key")
    PINECONE_ENVIRONMENT: str = Field(default="us-east-1", description="Pinecone environment/region")
    PINECONE_INDEX_NAME: str = Field(default="convergeai-docs", description="Pinecone index name")
    PINECONE_DIMENSION: int = Field(default=384, description="Embedding dimension (384 for all-MiniLM-L6-v2)")
    PINECONE_METRIC: str = Field(default="cosine", description="Distance metric")
    PINECONE_CLOUD: str = Field(default="aws", description="Cloud provider (aws, gcp, azure)")
    PINECONE_REGION: str = Field(default="us-east-1", description="Pinecone region")
    PINECONE_CAPACITY_MODE: str = Field(default="serverless", description="Capacity mode (serverless or pod)")

    # Google Generative AI (Gemini)
    GOOGLE_API_KEY: str = Field(..., description="Google Generative AI API key")
    GEMINI_MODEL_FLASH: str = Field(default="gemini-2.0-flash-exp", description="Gemini Flash model")
    GEMINI_MODEL_PRO: str = Field(default="gemini-1.5-pro", description="Gemini Pro model")
    GEMINI_TEMPERATURE: float = Field(default=0.7, description="LLM temperature")
    GEMINI_MAX_TOKENS: int = Field(default=2048, description="Max output tokens")
    GEMINI_TOP_P: float = Field(default=0.95, description="Top-p sampling")
    GEMINI_TOP_K: int = Field(default=40, description="Top-k sampling")

    # Embedding Model (Sentence Transformers)
    EMBEDDING_MODEL: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="Sentence Transformers embedding model"
    )
    EMBEDDING_DIMENSION: int = Field(default=384, description="Embedding dimension")
    EMBEDDING_BATCH_SIZE: int = Field(default=100, description="Batch size for embeddings")
    EMBEDDING_DEVICE: str = Field(default="cpu", description="Device for embeddings (cpu, cuda, mps)")
    EMBEDDING_NORMALIZE: bool = Field(default=True, description="Normalize embeddings")
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = Field(default=True, description="Enable rate limiting")
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, description="Requests per minute per user")
    RATE_LIMIT_PER_HOUR: int = Field(default=1000, description="Requests per hour per user")
    
    # File Upload
    MAX_UPLOAD_SIZE: int = Field(default=10 * 1024 * 1024, description="Max file upload size (10MB)")
    ALLOWED_UPLOAD_EXTENSIONS: str = Field(
        default=".pdf,.txt,.doc,.docx,.jpg,.jpeg,.png",
        description="Allowed file extensions (comma-separated)"
    )
    UPLOAD_DIR: str = Field(default="uploads", description="Upload directory")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format"
    )
    LOG_FILE: str = Field(default="logs/app.log", description="Log file path")
    LOG_MAX_BYTES: int = Field(default=10 * 1024 * 1024, description="Max log file size (10MB)")
    LOG_BACKUP_COUNT: int = Field(default=5, description="Number of log backup files")
    LOG_JSON: bool = Field(default=False, description="Use JSON logging format")
    
    # Celery (Background Tasks)
    CELERY_BROKER_URL: Optional[str] = Field(default=None, description="Celery broker URL (Redis)")
    CELERY_RESULT_BACKEND: Optional[str] = Field(default=None, description="Celery result backend")
    
    # Email (for notifications)
    SMTP_HOST: Optional[str] = Field(default=None, description="SMTP host")
    SMTP_PORT: Optional[int] = Field(default=587, description="SMTP port")
    SMTP_USER: Optional[str] = Field(default=None, description="SMTP username")
    SMTP_PASSWORD: Optional[str] = Field(default=None, description="SMTP password")
    SMTP_FROM_EMAIL: Optional[str] = Field(default=None, description="From email address")
    
    # SMS (for notifications)
    SMS_PROVIDER: Optional[str] = Field(default=None, description="SMS provider (twilio, aws_sns)")
    SMS_API_KEY: Optional[str] = Field(default=None, description="SMS API key")
    SMS_API_SECRET: Optional[str] = Field(default=None, description="SMS API secret")
    SMS_FROM_NUMBER: Optional[str] = Field(default=None, description="From phone number")
    
    # Monitoring
    SENTRY_DSN: Optional[str] = Field(default=None, description="Sentry DSN for error tracking")
    ENABLE_METRICS: bool = Field(default=True, description="Enable Prometheus metrics")
    
    # Security
    SECRET_KEY: str = Field(..., description="Application secret key")
    ALLOWED_HOSTS: str = Field(default="*", description="Allowed hosts (comma-separated)")
    
    # Cache TTL (Time To Live in seconds)
    CACHE_TTL_SHORT: int = Field(default=300, description="Short cache TTL (5 minutes)")
    CACHE_TTL_MEDIUM: int = Field(default=3600, description="Medium cache TTL (1 hour)")
    CACHE_TTL_LONG: int = Field(default=86400, description="Long cache TTL (24 hours)")
    
    # AI/Agent Settings
    MAX_CONVERSATION_HISTORY: int = Field(default=10, description="Max conversation history to include")
    INTENT_CONFIDENCE_THRESHOLD: float = Field(default=0.7, description="Minimum confidence for intent")
    ENABLE_STREAMING: bool = Field(default=True, description="Enable streaming responses")
    
    # Validators
    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_environment(cls, v):
        """Validate environment value"""
        allowed = ["development", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"ENVIRONMENT must be one of {allowed}")
        return v

    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v):
        """Validate log level"""
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed:
            raise ValueError(f"LOG_LEVEL must be one of {allowed}")
        return v.upper()
    
    @model_validator(mode='after')
    def build_urls(self):
        """Build Redis and Celery URLs if not provided"""
        # Build Redis URL if not provided
        if not self.REDIS_URL:
            host = self.REDIS_HOST
            port = self.REDIS_PORT
            db = self.REDIS_DB
            password = self.REDIS_PASSWORD

            if password:
                self.REDIS_URL = f"redis://:{password}@{host}:{port}/{db}"
            else:
                self.REDIS_URL = f"redis://{host}:{port}/{db}"

        # Build Celery broker URL if not provided
        if not self.CELERY_BROKER_URL:
            self.CELERY_BROKER_URL = self.REDIS_URL

        # Build Celery result backend if not provided
        if not self.CELERY_RESULT_BACKEND:
            self.CELERY_RESULT_BACKEND = self.REDIS_URL

        return self
    
    # Properties
    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.ENVIRONMENT == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.ENVIRONMENT == "production"

    @property
    def is_staging(self) -> bool:
        """Check if running in staging mode"""
        return self.ENVIRONMENT == "staging"

    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @property
    def cors_methods_list(self) -> List[str]:
        """Get CORS methods as list"""
        if self.CORS_ALLOW_METHODS == "*":
            return ["*"]
        return [method.strip() for method in self.CORS_ALLOW_METHODS.split(",")]

    @property
    def cors_headers_list(self) -> List[str]:
        """Get CORS headers as list"""
        if self.CORS_ALLOW_HEADERS == "*":
            return ["*"]
        return [header.strip() for header in self.CORS_ALLOW_HEADERS.split(",")]

    @property
    def allowed_extensions_list(self) -> List[str]:
        """Get allowed upload extensions as list"""
        return [ext.strip() for ext in self.ALLOWED_UPLOAD_EXTENSIONS.split(",")]

    @property
    def allowed_hosts_list(self) -> List[str]:
        """Get allowed hosts as list"""
        if self.ALLOWED_HOSTS == "*":
            return ["*"]
        return [host.strip() for host in self.ALLOWED_HOSTS.split(",")]
    
    # Model config
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance
    Use lru_cache to create singleton
    """
    return Settings()


# Export settings instance
settings = get_settings()

