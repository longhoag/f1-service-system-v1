"""Configuration settings loaded from environment variables"""
import os
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

class Settings:
    """Application settings from environment variables"""
    
    # OpenAI
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o")
    
    # AWS Bedrock
    aws_access_key_id: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    aws_secret_access_key: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    aws_region: str = os.getenv("AWS_REGION", "us-east-1")
    bedrock_kb_id: str = os.getenv("BEDROCK_KNOWLEDGE_BASE_ID", "")
    bedrock_embedding_model: str = os.getenv("BEDROCK_EMBEDDING_MODEL", "amazon.titan-embed-text-v2:0")
    bedrock_generation_model: str = os.getenv("BEDROCK_GENERATION_MODEL", "anthropic.claude-3-sonnet-20240229-v1:0")
    
    # Pinecone
    pinecone_api_key: str = os.getenv("PINECONE_API_KEY", "")
    pinecone_environment: str = os.getenv("PINECONE_ENVIRONMENT", "us-east-1")
    pinecone_index_name: str = os.getenv("PINECONE_INDEX_NAME", "f1-regulations")
    
    # Application
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    def validate(self) -> bool:
        """Validate required settings are present"""
        required = {
            "AWS_ACCESS_KEY_ID": self.aws_access_key_id,
            "AWS_SECRET_ACCESS_KEY": self.aws_secret_access_key,
            "BEDROCK_KNOWLEDGE_BASE_ID": self.bedrock_kb_id,
        }
        
        missing = [key for key, value in required.items() if not value]
        
        if missing:
            logger.error(f"Missing required environment variables: {', '.join(missing)}")
            return False
        
        logger.info("✅ All required settings validated")
        return True

settings = Settings()
