"""
Application settings and environment variable management.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger

# Load environment variables from .env file
load_dotenv()


class Settings:
    """
    Application configuration loaded from environment variables.
    """

    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # AWS Bedrock Configuration
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    BEDROCK_KNOWLEDGE_BASE_ID: str = os.getenv("BEDROCK_KNOWLEDGE_BASE_ID", "")

    # Pinecone Configuration
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "")
    PINECONE_ENVIRONMENT: str = os.getenv("PINECONE_ENVIRONMENT", "")
    PINECONE_INDEX_NAME: str = os.getenv("PINECONE_INDEX_NAME", "f1-regulations")

    # Application Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Circuit maps directory
    CIRCUIT_MAPS_DIR: Path = Path(__file__).parent.parent.parent / "f1_2025_circuit_maps"

    @classmethod
    def validate(cls):
        """Validate that required environment variables are set."""
        required_vars = [
            "OPENAI_API_KEY",
            "AWS_ACCESS_KEY_ID", 
            "AWS_SECRET_ACCESS_KEY",
            "PINECONE_API_KEY"
        ]
        
        missing_vars = [var for var in required_vars if not getattr(cls, var)]
        
        if missing_vars:
            logger.warning("Missing required environment variables: {}", missing_vars)
            return False
        
        return True


# Create global settings instance
settings = Settings()
