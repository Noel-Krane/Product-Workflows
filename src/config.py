"""
Configuration management for AI Research Platform
Centralized configuration using Pydantic Settings
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional, List, Dict, Any
import os


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application
    environment: str = Field(default="development", description="Environment: development, staging, production")
    host: str = Field(default="0.0.0.0", description="Host to bind the application")
    port: int = Field(default=8000, description="Port to bind the application")
    debug: bool = Field(default=True, description="Debug mode")
    
    # Database
    database_url: str = Field(default="sqlite:///./ai_research_platform.db", description="Database connection URL")
    
    # API Keys
    openrouter_api_key: Optional[str] = Field(default=None, description="OpenRouter API key for LLM access")
    openrouter_base_url: str = Field(default="https://openrouter.ai/api/v1", description="OpenRouter base URL")
    
    perplexity_api_key: Optional[str] = Field(default=None, description="Perplexity API key for research")
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic API key")
    
    # LangSmith Configuration
    langchain_tracing_v2: bool = Field(default=True, description="Enable LangSmith tracing")
    langchain_endpoint: str = Field(default="https://api.smith.langchain.com", description="LangSmith endpoint")
    langchain_api_key: Optional[str] = Field(default=None, description="LangSmith API key")
    langchain_project: str = Field(default="ai-research-platform", description="LangSmith project name")
    
    # Cost Control
    api_budget_soft_cap: float = Field(default=50.0, description="Soft budget cap in USD")
    api_budget_hard_cap: float = Field(default=100.0, description="Hard budget cap in USD")
    
    # Model Configuration
    default_research_model: str = Field(default="anthropic/claude-3.5-sonnet", description="Default model for research")
    default_analysis_model: str = Field(default="anthropic/claude-3.5-sonnet", description="Default model for analysis")
    fallback_model: str = Field(default="openai/gpt-4o-mini", description="Fallback model")
    
    # WebSocket
    websocket_port: int = Field(default=8001, description="WebSocket port for real-time updates")
    
    # CORS
    frontend_url: str = Field(default="http://localhost:3000", description="Frontend URL for CORS")
    allowed_origins: List[str] = Field(default=["http://localhost:3000", "http://localhost:3001"], description="Allowed CORS origins")
    
    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(default="json", description="Log format: json or text")
    
    # Rate Limiting
    requests_per_minute: int = Field(default=30, description="Rate limit: requests per minute")
    tokens_per_minute: int = Field(default=100000, description="Rate limit: tokens per minute")
    
    # Research Configuration
    max_research_depth: int = Field(default=3, description="Maximum research depth")
    max_sources_per_query: int = Field(default=10, description="Maximum sources per research query")
    citation_required: bool = Field(default=True, description="Require citations in research output")
    
    # Security
    secret_key: str = Field(default="dev-secret-key-change-in-production", description="Secret key for security")
    access_token_expire_minutes: int = Field(default=1440, description="Access token expiration in minutes")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


# Model cost mapping (USD per 1K tokens)
MODEL_COSTS = {
    "anthropic/claude-3.5-sonnet": {
        "input": 0.003,
        "output": 0.015
    },
    "anthropic/claude-3-haiku": {
        "input": 0.00025,
        "output": 0.00125
    },
    "openai/gpt-4o": {
        "input": 0.005,
        "output": 0.015
    },
    "openai/gpt-4o-mini": {
        "input": 0.00015,
        "output": 0.0006
    },
    "perplexity/llama-3.1-sonar-large-128k-online": {
        "input": 0.001,
        "output": 0.001
    }
}

# Research framework configuration
RESEARCH_FRAMEWORKS = {
    "porters": {
        "name": "Porter's Five Forces",
        "components": ["competitive_rivalry", "supplier_power", "buyer_power", "threat_of_substitutes", "threat_of_new_entrants"],
        "description": "Competitive environment analysis"
    },
    "pestel": {
        "name": "PESTEL Analysis",
        "components": ["political", "economic", "social", "technological", "environmental", "legal"],
        "description": "Macro environment analysis"
    },
    "swot": {
        "name": "SWOT Analysis",
        "components": ["strengths", "weaknesses", "opportunities", "threats"],
        "description": "Strategic positioning analysis"
    },
    "ansoff": {
        "name": "Ansoff Matrix",
        "components": ["market_penetration", "product_development"],  # Focused on these two
        "description": "Growth opportunity analysis"
    },
    "vpc": {
        "name": "Value Proposition Canvas",
        "components": ["customer_jobs", "pain_points", "gains", "value_mapping"],
        "description": "Customer value analysis"
    }
}

# Trusted source weighting
SOURCE_WEIGHTS = {
    "academic": 1.0,
    "industry_report": 0.9,
    "construction_tech_publication": 0.8,
    "ai_tech_newsletter": 0.7,
    "linkedin_influencer": 0.6,
    "news_media": 0.5,
    "blog": 0.3,
    "unknown": 0.1
}