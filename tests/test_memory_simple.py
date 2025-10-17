"""
Quick test of conversation memory with circuit queries only (fast, no Bedrock).
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from loguru import logger
from src.agents.orchestrator import get_orchestrator
from src.utils.logger import setup_logger


def test_circuit_memory():
    """Test orchestrator memory with circuit queries (fast, no Bedrock)."""
    setup_logger()
    
    orchestrator = get_orchestrator()
    
    logger.info("🧠 Testing Conversation Memory with Circuits (Fast Test)\n")
    logger.info("="*70)
    
    conversation_history = []
    
    # Query 1: Ask for Monaco
    logger.info("\n📝 Query 1: Initial circuit request")
    logger.info("-" * 70)
    query1 = "Show me Monaco circuit"
    logger.info(f"User: {query1}")
    logger.info(f"Memory: {len(conversation_history)} messages")
    
    result1 = orchestrator.process_query(query1, conversation_history=conversation_history)
    response1 = result1.get('content', '')
    logger.info(f"Assistant: {response1[:100]}...")
    logger.info(f"Tools used: {result1.get('tools_used', [])}")
    
    # Update history
    conversation_history.append({"role": "user", "content": query1})
    conversation_history.append({"role": "assistant", "content": response1})
    logger.success(f"✓ Memory updated: {len(conversation_history)} messages")
    
    # Query 2: Follow-up using "that circuit" (requires context)
    logger.info("\n📝 Query 2: Follow-up about 'that circuit' (WITH memory)")
    logger.info("-" * 70)
    query2 = "What country is that circuit in?"
    logger.info(f"User: {query2}")
    logger.info(f"Memory: {len(conversation_history)} messages (Monaco context)")
    
    result2 = orchestrator.process_query(query2, conversation_history=conversation_history)
    response2 = result2.get('content', '')
    logger.info(f"Assistant: {response2[:150]}...")
    logger.info(f"Tools used: {result2.get('tools_used', [])}")
    
    # Update history
    conversation_history.append({"role": "user", "content": query2})
    conversation_history.append({"role": "assistant", "content": response2})
    logger.success(f"✓ Memory updated: {len(conversation_history)} messages")
    
    # Query 3: Switch to different circuit
    logger.info("\n📝 Query 3: Switch to different circuit")
    logger.info("-" * 70)
    query3 = "Now show me Silverstone"
    logger.info(f"User: {query3}")
    logger.info(f"Memory: {len(conversation_history)} messages")
    
    result3 = orchestrator.process_query(query3, conversation_history=conversation_history)
    response3 = result3.get('content', '')
    logger.info(f"Assistant: {response3[:100]}...")
    logger.info(f"Tools used: {result3.get('tools_used', [])}")
    
    # Update history
    conversation_history.append({"role": "user", "content": query3})
    conversation_history.append({"role": "assistant", "content": response3})
    logger.success(f"✓ Memory updated: {len(conversation_history)} messages")
    
    # Query 4: Follow-up should now refer to Silverstone, not Monaco
    logger.info("\n📝 Query 4: Follow-up about 'it' (should be Silverstone)")
    logger.info("-" * 70)
    query4 = "What's the official name of it?"
    logger.info(f"User: {query4}")
    logger.info(f"Memory: {len(conversation_history)} messages (context switched to Silverstone)")
    
    result4 = orchestrator.process_query(query4, conversation_history=conversation_history)
    response4 = result4.get('content', '')
    logger.info(f"Assistant: {response4[:150]}...")
    logger.info(f"Tools used: {result4.get('tools_used', [])}")
    
    # Summary
    logger.info("\n" + "="*70)
    logger.info("✅ CONVERSATION MEMORY TEST COMPLETE")
    logger.info("="*70)
    logger.info(f"\nTotal queries: 4")
    logger.info(f"Total messages: {len(conversation_history)}")
    logger.info(f"Exchanges: {len(conversation_history) // 2}")
    
    logger.info("\n📊 Expected Behavior:")
    logger.info("  ✓ Query 2 should understand 'that circuit' = Monaco")
    logger.info("  ✓ Query 4 should understand 'it' = Silverstone (not Monaco)")
    logger.info("  ✓ Memory tracks conversation context across topic switches")
    
    logger.info("\n🧠 Memory Status:")
    logger.info(f"  • Stored messages: {len(conversation_history)}")
    logger.info(f"  • User messages: {len([m for m in conversation_history if m['role'] == 'user'])}")
    logger.info(f"  • Assistant messages: {len([m for m in conversation_history if m['role'] == 'assistant'])}")


def test_without_memory():
    """Test the same follow-up WITHOUT memory (should fail)."""
    logger.info("\n\n" + "="*70)
    logger.info("🚫 Testing WITHOUT Memory (for comparison)")
    logger.info("="*70)
    
    orchestrator = get_orchestrator()
    
    logger.info("\n📝 Follow-up query WITHOUT any context")
    logger.info("-" * 70)
    query = "What country is that circuit in?"
    logger.info(f"User: {query}")
    logger.info("Memory: NONE (empty history)")
    
    result = orchestrator.process_query(query, conversation_history=[])
    response = result.get('content', '')
    logger.info(f"Assistant: {response[:200]}...")
    logger.info(f"Tools used: {result.get('tools_used', [])}")
    
    logger.info("\n⚠️  Without memory:")
    logger.info("   • Agent doesn't know what 'that circuit' refers to")
    logger.info("   • No context from previous conversation")
    logger.info("   • Response should indicate confusion or ask for clarification")


if __name__ == "__main__":
    test_circuit_memory()
    test_without_memory()
