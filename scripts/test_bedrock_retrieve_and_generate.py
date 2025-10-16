"""Test Bedrock Knowledge Base retrieval AND answer generation"""
import sys
import os
import boto3
import time
from loguru import logger

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config.settings import settings
from src.utils.logger import setup_logger

def test_retrieve_and_generate():
    """Test retrieval + answer generation from Bedrock Knowledge Base"""
    
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
    
    # Test queries requiring answer synthesis
    test_queries = [
        {
            "query": "according to financial regulations, when the financial regulations came into force?",
            "expected_keywords": ["financial regulations", "into force"]
        },
        {
            "query": "How much points will be awarded for 1st position?",
            "expected_keywords": ["points", "position", "awarded"]
        },
    ]
    
    logger.info(f"Testing {len(test_queries)} queries with answer generation")
    logger.info(f"Knowledge Base ID: {settings.bedrock_kb_id}")
    logger.info(f"Generation Model: {settings.bedrock_generation_model}")
    
    results_summary = []
    
    for idx, test_case in enumerate(test_queries, 1):
        query = test_case["query"]
        expected_keywords = test_case.get("expected_keywords", [])
        
        logger.info(f"\n{'='*70}")
        logger.info(f"Test {idx}/{len(test_queries)}: {query}")
        logger.info(f"{'='*70}")
        
        try:
            start_time = time.time()
            
            # Retrieve AND generate answer using configured generation model
            response = bedrock_agent.retrieve_and_generate(
                input={"text": query},
                retrieveAndGenerateConfiguration={
                    "type": "KNOWLEDGE_BASE",
                    "knowledgeBaseConfiguration": {
                        "knowledgeBaseId": settings.bedrock_kb_id,
                        "modelArn": f"arn:aws:bedrock:{settings.aws_region}::foundation-model/{settings.bedrock_generation_model}",
                        "generationConfiguration": {
                            "inferenceConfig": {
                                "textInferenceConfig": {
                                    "maxTokens": 2048,
                                    "temperature": 0.7
                                }
                            }
                        },
                        "retrievalConfiguration": {
                            "vectorSearchConfiguration": {
                                "numberOfResults": 3
                            }
                        }
                    }
                }
            )
            
            elapsed_time = time.time() - start_time
            
            # Extract generated answer
            answer = response.get('output', {}).get('text', 'No answer generated')
            citations = response.get('citations', [])
            
            logger.success(f"\n📝 Generated Answer ({elapsed_time:.2f}s):")
            logger.info(f"{answer}\n")
            
            # Display sources
            if citations:
                logger.info(f"📚 Sources ({len(citations)} citations):")
                
                unique_sources = set()
                for citation in citations:
                    for ref in citation.get('retrievedReferences', []):
                        source_uri = ref.get('location', {}).get('s3Location', {}).get('uri', 'Unknown')
                        filename = source_uri.split('/')[-1] if '/' in source_uri else source_uri
                        
                        if filename not in unique_sources:
                            unique_sources.add(filename)
                            logger.info(f"  • {filename}")
            else:
                logger.warning("⚠️ No citations provided")
            
            # Validate answer quality
            answer_lower = answer.lower()
            keywords_found = sum(1 for kw in expected_keywords if kw.lower() in answer_lower)
            keyword_coverage = (keywords_found / len(expected_keywords) * 100) if expected_keywords else 100
            
            logger.info(f"Keyword Coverage: {keywords_found}/{len(expected_keywords)} ({keyword_coverage:.1f}%)")
            
            # Answer quality assessment
            if keyword_coverage >= 75 and len(answer) > 100:
                logger.success("✅ High quality answer")
                quality = "high"
            elif keyword_coverage >= 50 and len(answer) > 50:
                logger.info("✓ Adequate answer quality")
                quality = "medium"
            else:
                logger.warning("⚠️ Answer may lack detail or relevance")
                quality = "low"
            
            results_summary.append({
                "query": query,
                "status": "success",
                "quality": quality,
                "keyword_coverage": keyword_coverage,
                "answer_length": len(answer),
                "citations": len(citations),
                "response_time": elapsed_time
            })
            
            # Rate limiting: wait between requests
            logger.debug("Waiting 10 seconds to avoid rate limits...")
            time.sleep(10)
            
        except Exception as e:
            logger.error(f"❌ Retrieve and generate failed: {e}")
            
            # Check if it's a throttling error
            if "ThrottlingException" in str(e) or "429" in str(e):
                logger.warning("Rate limit hit. Waiting 15 seconds before continuing...")
                time.sleep(15)
            
            results_summary.append({
                "query": query,
                "status": "error",
                "error": str(e)
            })
    
    # Print summary
    logger.info("\n" + "="*70)
    logger.info("RETRIEVE & GENERATE TEST SUMMARY")
    logger.info("="*70)
    
    for result in results_summary:
        query_short = result['query'][:50] + "..." if len(result['query']) > 50 else result['query']
        
        if result['status'] == 'success':
            quality_icon = "✅" if result['quality'] == 'high' else "✓" if result['quality'] == 'medium' else "⚠️"
            logger.info(f"{quality_icon} {query_short}")
            logger.info(f"   Quality: {result['quality']} | Keywords: {result['keyword_coverage']:.0f}% | "
                       f"Length: {result['answer_length']} chars | Citations: {result['citations']} | "
                       f"Time: {result['response_time']:.2f}s")
        else:
            logger.error(f"❌ {query_short}")
            logger.error(f"   Error: {result.get('error', 'Unknown')}")
    
    # Calculate success metrics
    successful = sum(1 for r in results_summary if r['status'] == 'success')
    high_quality = sum(1 for r in results_summary if r.get('quality') == 'high')
    
    success_rate = (successful / len(results_summary)) * 100
    quality_rate = (high_quality / len(results_summary)) * 100 if results_summary else 0
    
    avg_time = sum(r.get('response_time', 0) for r in results_summary if r['status'] == 'success') / max(successful, 1)
    
    logger.info(f"\nSuccess Rate: {successful}/{len(results_summary)} ({success_rate:.1f}%)")
    logger.info(f"High Quality Rate: {high_quality}/{len(results_summary)} ({quality_rate:.1f}%)")
    logger.info(f"Average Response Time: {avg_time:.2f}s")
    
    if success_rate >= 80 and quality_rate >= 60:
        logger.success("🎉 Excellent RAG performance!")
    elif success_rate >= 60:
        logger.info("👍 Good RAG performance")
    else:
        logger.warning("⚠️ Consider tuning retrieval or generation parameters")

if __name__ == "__main__":
    logger.info("Starting Bedrock Knowledge Base retrieve + generate test...")
    test_retrieve_and_generate()
