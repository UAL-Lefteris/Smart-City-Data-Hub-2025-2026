import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Attributes:
        DATABASE_URL: PostgreSQL connection string
        POSTGRES_USER: Database user
        POSTGRES_PASSWORD: Database password
        POSTGRES_DB: Database name
        POSTGRES_HOST: Database host
        POSTGRES_PORT: Database port
        API_V1_PREFIX: API version prefix
        PROJECT_NAME: Project name
    """

    # PostgreSQL Configuration
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "urban_data_hub"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432

    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Urban Data Hub API"

    # MongoDB Configuration (for future lectures)
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB: str = "urban_data_hub"

    @property
    def DATABASE_URL(self) -> str:
        """
        Construct PostgreSQL connection URL from components.

        Returns:
            str: Complete database URL
        """
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()
