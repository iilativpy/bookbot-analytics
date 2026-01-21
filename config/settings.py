"""
Configuration settings for the Telegram Booking Bot.
Supports multiple booking sites through templating.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Config(BaseSettings):
    """
    Application configuration with environment variable support.
    Site name and AI model are configurable for easy reuse.
    """
    
    # Site Configuration (Template - easily changeable)
    site_name: str = Field(default="Your Booking Site", alias="SITE_NAME")
    
    # Telegram Configuration
    telegram_bot_token: str = Field(..., alias="TELEGRAM_BOT_TOKEN")
    
    # OpenRouter API Configuration (Universal - easily changeable)
    openrouter_api_key: str = Field(..., alias="OPENROUTER_API_KEY")
    openrouter_model: str = Field(
        default="deepseek/deepseek-v3",
        alias="OPENROUTER_MODEL"
    )
    openrouter_base_url: str = Field(
        default="https://openrouter.ai/api/v1",
        alias="OPENROUTER_BASE_URL"
    )
    
    # MySQL Database Configuration
    mysql_host: str = Field(default="localhost", alias="MYSQL_HOST")
    mysql_port: int = Field(default=3306, alias="MYSQL_PORT")
    mysql_user: str = Field(..., alias="MYSQL_USER")
    mysql_password: str = Field(..., alias="MYSQL_PASSWORD")
    mysql_database: str = Field(..., alias="MYSQL_DATABASE")
    
    # Application Settings
    timezone: str = Field(default="UTC", alias="TIMEZONE")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    max_conversation_history: int = Field(default=10, alias="MAX_CONVERSATION_HISTORY")
    
    # Prediction Settings
    prediction_confidence_interval: float = Field(
        default=0.95,
        alias="PREDICTION_CONFIDENCE_INTERVAL"
    )
    min_historical_days: int = Field(default=30, alias="MIN_HISTORICAL_DAYS")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    @property
    def database_url(self) -> str:
        """Generate SQLAlchemy database URL."""
        return (
            f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
        )
    
    def get_welcome_message(self) -> str:
        """Generate welcome message with site name."""
        return f"""
Welcome to {self.site_name} Booking Statistics Bot! 🎉

I can help you analyze booking data, generate predictions, and provide insights.

Available commands:
/stats - Current month statistics
/compare - Compare different time periods
/predict - Booking predictions
/trends - Trend analysis
/cancellations - Cancellation statistics
/returns - Return customer analysis
/help - Show all commands

You can also ask me questions in natural language, like:
• "How many bookings did we have last month?"
• "Compare this month with last year"
• "What's our cancellation rate?"
• "Predict bookings for next week"
"""


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """
    Get or create the global configuration instance.
    
    Returns:
        Config: The application configuration
    """
    global _config
    if _config is None:
        _config = Config()
    return _config
