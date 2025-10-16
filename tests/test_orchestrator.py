"""Test the F1 Agent Orchestrator with LangGraph and LangSmith tracing"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agents.orchestrator import get_orchestrator
from src.utils.logger import setup_logger
from loguru import logger


def test_orchestrator():
    """Test the F1 orchestrator with different query types"""
    
    setup_logger()
    
    logger.info("="*70)
    logger.info("Testing F1 Agent Orchestrator with LangGraph + LangSmith")
    logger.info("="*70)
    
    # Initialize orchestrator
    orchestrator = get_orchestrator()
    
    # Test queries covering different intents
    test_queries = [
        {
            "query": "Show me the Monaco circuit",
            "expected_intent": "circuit",
            "description": "Circuit-only query"
        },
        {
            "query": "How many points for 1st position?",
            "expected_intent": "regulations",
            "description": "Points system query"
        },
        {
            "query": "Show me Silverstone and explain the safety car procedure",
            "expected_intent": "both",
            "description": "Combined circuit + regulations query"
        },
        {
            "query": "What's the penalty for a false start?",
            "expected_intent": "regulations",
            "description": "Penalty query"
        }
    ]
    
    results = []
    
    for idx, test_case in enumerate(test_queries, 1):
        query = test_case["query"]
        expected_intent = test_case["expected_intent"]
        description = test_case["description"]
        
        logger.info(f"\n{'='*70}")
        logger.info(f"Test {idx}/{len(test_queries)}: {description}")
        logger.info(f"Query: '{query}'")
        logger.info(f"Expected intent: {expected_intent}")
        logger.info(f"{'='*70}")
        
        try:
            # Process query through orchestrator
            result = orchestrator.process_query(query)
            
            actual_intent = result["intent"]
            response = result["response"]
            metadata = result["metadata"]
            
            # Log results
            logger.info(f"\n✓ Actual intent: {actual_intent}")
            
            if actual_intent == expected_intent:
                logger.success(f"✓ Intent classification CORRECT")
            else:
                logger.warning(
                    f"⚠️  Intent mismatch: expected '{expected_intent}', "
                    f"got '{actual_intent}'"
                )
            
            logger.info(f"Circuit executed: {metadata['circuit_executed']}")
            logger.info(f"Regulations executed: {metadata['regulations_executed']}")
            
            # Display response based on type
            response_type = response.get("type") if isinstance(response, dict) else "unknown"
            logger.info(f"Response type: {response_type}")
            
            if response_type == "image":
                logger.success(f"📸 Image: {response.get('message')}")
                logger.info(f"   Path: {response['content']}")
            elif response_type == "text":
                content = response.get("content", "")
                logger.success(f"📝 Text response ({len(content)} chars):")
                logger.info(f"   {content[:200]}..." if len(content) > 200 else content)
                
                # Show sources if available
                sources = response.get("metadata", {}).get("sources", [])
                if sources:
                    logger.info(f"   Sources: {', '.join(sources)}")
            elif response_type == "combined":
                logger.success(f"🔄 Combined response:")
                logger.info(f"   Circuit: {response.get('circuit', {}).get('type')}")
                logger.info(f"   Regulations: {response.get('regulations', {}).get('type')}")
            else:
                logger.info(f"Response: {response}")
            
            results.append({
                "query": query,
                "expected_intent": expected_intent,
                "actual_intent": actual_intent,
                "correct": actual_intent == expected_intent,
                "response_type": response_type,
                "status": "success"
            })
            
        except Exception as e:
            logger.error(f"❌ Test failed with error: {e}")
            results.append({
                "query": query,
                "expected_intent": expected_intent,
                "status": "error",
                "error": str(e)
            })
    
    # Summary
    logger.info(f"\n{'='*70}")
    logger.info("TEST SUMMARY")
    logger.info(f"{'='*70}")
    
    successful = sum(1 for r in results if r.get("status") == "success")
    correct_intents = sum(1 for r in results if r.get("correct"))
    
    logger.info(f"Tests completed: {successful}/{len(results)}")
    logger.info(f"Correct intent classification: {correct_intents}/{len(results)}")
    
    if successful == len(results) and correct_intents == len(results):
        logger.success("🎉 All tests passed!")
    elif successful == len(results):
        logger.warning("⚠️  All tests executed but some intent classifications were off")
    else:
        logger.error("❌ Some tests failed")
    
    # Display LangSmith tracing info
    logger.info(f"\n{'='*70}")
    logger.info("LangSmith Tracing")
    logger.info(f"{'='*70}")
    logger.info("Check your LangSmith dashboard for detailed traces:")
    logger.info("https://smith.langchain.com/")
    logger.info("\nTraces include:")
    logger.info("  - Intent classification")
    logger.info("  - Tool execution (circuit retrieval / regulations RAG)")
    logger.info("  - Bedrock API calls")
    logger.info("  - Response synthesis")


if __name__ == "__main__":
    test_orchestrator()
