"""Test Bedrock Knowledge Base retrieval (chunks only, no generation)"""
import sys
import os
import boto3
from loguru import logger

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config.settings import settings
from src.utils.logger import setup_logger

def test_retrieve():
    """Test basic retrieval from Bedrock Knowledge Base"""
    
    # Setup logger
    setup_logger()
    
    # Validate settings
    if not settings.validate():
        logger.error("Configuration validation failed. Check your .env file.")
        return
    
    # Initialize Bedrock Agent Runtime client
    logger.info("Initializing Bedrock Agent Runtime client...")
    bedrock_agent = boto3.client(
        'bedrock-agent-runtime',
        region_name=settings.aws_region,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key
    )
    
    # Test queries covering different regulation types
    test_queries = [
        "How much points will be awarded for 1st position?",
        "When did the financial regulations come into force?",
    ]
    
    logger.info(f"Testing {len(test_queries)} queries against Knowledge Base")
    logger.info(f"Knowledge Base ID: {settings.bedrock_kb_id}")
    
    results_summary = []
    
    for idx, query in enumerate(test_queries, 1):
        logger.info(f"\n{'='*70}")
        logger.info(f"Test {idx}/{len(test_queries)}: {query}")
        logger.info(f"{'='*70}")
        
        try:
            # Retrieve relevant chunks
            response = bedrock_agent.retrieve(
                knowledgeBaseId=settings.bedrock_kb_id,
                retrievalQuery={"text": query},
                retrievalConfiguration={
                    "vectorSearchConfiguration": {
                        "numberOfResults": 3
                    }
                }
            )
            
            results = response.get('retrievalResults', [])
            logger.info(f"Retrieved {len(results)} chunks")
            
            if not results:
                logger.warning("⚠️ No results found")
                results_summary.append({
                    "query": query,
                    "status": "no_results",
                    "avg_score": 0.0
                })
                continue
            
            # Display retrieved chunks
            for i, chunk in enumerate(results, 1):
                score = chunk.get('score', 0.0)
                # Handle different content structures
                content = chunk.get('content', {})
                text = content.get('text', '') if isinstance(content, dict) else str(content)
                source = chunk.get('location', {}).get('s3Location', {}).get('uri', 'Unknown')
                
                # Extract filename from S3 URI
                filename = source.split('/')[-1] if '/' in source else source
                
                logger.info(f"\n--- Chunk {i} (Score: {score:.3f}) ---")
                logger.info(f"Source: {filename}")
                logger.info(f"Content Preview: {text[:200]}...")
                
                # Check if chunk has metadata
                metadata = chunk.get('metadata', {})
                if metadata:
                    logger.debug(f"Metadata: {metadata}")
            
            # Calculate average score
            avg_score = sum(c.get('score', 0.0) for c in results) / len(results)
            
            if avg_score >= 0.7:
                logger.success(f"✅ High relevance - Average score: {avg_score:.3f}")
                status = "high_relevance"
            elif avg_score >= 0.5:
                logger.info(f"✓ Medium relevance - Average score: {avg_score:.3f}")
                status = "medium_relevance"
            else:
                logger.warning(f"⚠️ Low relevance - Average score: {avg_score:.3f}")
                status = "low_relevance"
            
            results_summary.append({
                "query": query,
                "status": status,
                "avg_score": avg_score,
                "chunks_retrieved": len(results)
            })
            
        except Exception as e:
            logger.error(f"❌ Retrieval failed: {e}")
            
            # Check for specific error types
            if "ThrottlingException" in str(e) or "429" in str(e):
                logger.warning("Rate limit hit. Waiting 10 seconds before continuing...")
                import time
                time.sleep(10)
            
            results_summary.append({
                "query": query,
                "status": "error",
                "error": str(e)
            })
    
    # Print summary
    logger.info("\n" + "="*70)
    logger.info("RETRIEVAL TEST SUMMARY")
    logger.info("="*70)
    
    for result in results_summary:
        query_short = result['query'][:50] + "..." if len(result['query']) > 50 else result['query']
        
        if result['status'] == 'high_relevance':
            logger.success(f"✅ {query_short} | Score: {result['avg_score']:.3f}")
        elif result['status'] == 'medium_relevance':
            logger.info(f"✓ {query_short} | Score: {result['avg_score']:.3f}")
        elif result['status'] == 'low_relevance':
            logger.warning(f"⚠️ {query_short} | Score: {result['avg_score']:.3f}")
        elif result['status'] == 'no_results':
            logger.warning(f"⚠️ {query_short} | No results")
        else:
            logger.error(f"❌ {query_short} | Error: {result.get('error', 'Unknown')}")
    
    # Calculate success rate
    successful = sum(1 for r in results_summary if r['status'] in ['high_relevance', 'medium_relevance'])
    success_rate = (successful / len(results_summary)) * 100
    
    logger.info(f"\nSuccess Rate: {successful}/{len(results_summary)} ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        logger.success("🎉 Excellent retrieval performance!")
    elif success_rate >= 60:
        logger.info("👍 Good retrieval performance")
    else:
        logger.warning("⚠️ Consider improving chunk quality or query formulation")

if __name__ == "__main__":
    logger.info("Starting Bedrock Knowledge Base retrieval test...")
    test_retrieve()
