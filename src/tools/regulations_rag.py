
    llm = ChatOpenAI(model="gpt-4o-mini").bind_tools([get_current_time, tavily_tool])"""
F1 Regulations RAG tool.

Uses AWS Bedrock Knowledge Base RetrieveAndGenerate API.
Single-call architecture optimized for speed and reliability.

Architecture Decision (see docs/ACCURACY_COMPARISON.md):
- Bedrock RetrieveAndGenerate: 4.7s avg, better retrieval, 4x cheaper
- Bedrock Retrieve + GPT-4o: 7.2s avg, better formatting, worse retrieval
- Decision: Use RetrieveAndGenerate (retrieval quality > formatting)

All operations traced with LangSmith for observability.
"""

import boto3
import time
from typing import Dict, Any, Optional
from botocore.exceptions import ClientError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from langsmith import traceable
from loguru import logger

from src.config.settings import settings


class RegulationsRAG:
    """
    RAG tool for F1 regulations queries using AWS Bedrock Knowledge Base.
    
    Uses RetrieveAndGenerate API for optimized single-call retrieval + generation.
    Implements LangSmith tracing for full observability.
    
    Based on comprehensive testing:
    - Average response time: 4.7s
    - Superior retrieval quality vs multi-step approaches
    - Cost-effective: ~$3/1M tokens (4x cheaper than GPT-4o)
    """

    def __init__(self):
        """Initialize AWS Bedrock Agent Runtime client."""
        logger.info("Initializing Regulations RAG tool (Bedrock RetrieveAndGenerate)")
        
        # Validate configuration
        if not settings.validate():
            raise ValueError("Invalid configuration. Check environment variables.")
        
        # Initialize Bedrock Agent Runtime client
        self.bedrock_agent = boto3.client(
            'bedrock-agent-runtime',
            region_name=settings.aws_region,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key
        )
        
        self.kb_id = settings.bedrock_kb_id
        self.model_arn = f"arn:aws:bedrock:{settings.aws_region}::foundation-model/{settings.bedrock_generation_model}"
        
        logger.success("Regulations RAG tool initialized")
        logger.info(f"  • Bedrock KB: {self.kb_id}")
        logger.info(f"  • Model: {settings.bedrock_generation_model}")

    @traceable(name="query_regulations", tags=["rag", "bedrock", "regulations"])
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(ClientError),
        reraise=True
    )
    def query_regulations(
        self,
        question: str,
        num_results: int = 5,
        max_tokens: int = 1500,
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """
        Query F1 regulations knowledge base using Bedrock RetrieveAndGenerate.
        
        Single API call that handles both retrieval and generation.
        Optimized for production use with fast response times.
        
        Args:
            question: F1 regulations question
            num_results: Number of chunks to retrieve (default: 5)
            max_tokens: Maximum tokens in generated response (default: 1500)
            temperature: Generation temperature (default: 0.3 for factual)
            
        Returns:
            Dict with type, content (answer), and metadata (citations, latency)
        """
        logger.info(f"Querying regulations: '{question}'")
        start_time = time.time()
        
        try:
            # Call Bedrock RetrieveAndGenerate API
            response = self.bedrock_agent.retrieve_and_generate(
                input={
                    'text': question
                },
                retrieveAndGenerateConfiguration={
                    'type': 'KNOWLEDGE_BASE',
                    'knowledgeBaseConfiguration': {
                        'knowledgeBaseId': self.kb_id,
                        'modelArn': self.model_arn,
                        'retrievalConfiguration': {
                            'vectorSearchConfiguration': {
                                'numberOfResults': num_results
                            }
                        },
                        'generationConfiguration': {
                            'inferenceConfig': {
                                'textInferenceConfig': {
                                    'maxTokens': max_tokens,
                                    'temperature': temperature
                                }
                            }
                        }
                    }
                }
            )
            
            elapsed_time = time.time() - start_time
            
            # Extract answer
            answer = response.get('output', {}).get('text', 'No answer generated')
            
            # Extract citations
            citations = []
            for citation in response.get('citations', []):
                for reference in citation.get('retrievedReferences', []):
                    citations.append({
                        'content': reference.get('content', {}).get('text', ''),
                        'location': reference.get('location', {}),
                        'metadata': reference.get('metadata', {})
                    })
            
            logger.success(f"Regulations query completed in {elapsed_time:.2f}s")
            logger.info(f"  • Answer length: {len(answer)} chars")
            logger.info(f"  • Citations: {len(citations)}")
            
            return {
                'type': 'text',
                'content': answer,
                'metadata': {
                    'status': 'success',
                    'question': question,
                    'latency_seconds': elapsed_time,
                    'citations': citations,
                    'num_results': num_results,
                    'model': settings.bedrock_generation_model
                }
            }
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            error_msg = e.response.get('Error', {}).get('Message', str(e))
            
            logger.error(f"Bedrock API error: {error_code} - {error_msg}")
            
            return {
                'type': 'error',
                'content': f"Bedrock API error: {error_msg}",
                'metadata': {
                    'status': 'error',
                    'error_code': error_code,
                    'error_message': error_msg,
                    'question': question
                }
            }
            
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            
            return {
                'type': 'error',
                'content': f"Unexpected error: {str(e)}",
                'metadata': {
                    'status': 'error',
                    'error': str(e),
                    'question': question
                }
            }


# Singleton instance
_regulations_rag_instance: Optional[RegulationsRAG] = None


def get_regulations_rag() -> RegulationsRAG:
    """Get or create singleton instance of RegulationsRAG."""
    global _regulations_rag_instance
    
    if _regulations_rag_instance is None:
        _regulations_rag_instance = RegulationsRAG()
    
    return _regulations_rag_instance
