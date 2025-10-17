"""
Test conversation memory with follow-up questions.
Demonstrates how the orchestrator uses conversation history for context.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from loguru import logger
from src.agents.orchestrator import get_orchestrator
from src.utils.logger import setup_logger


def test_conversation_memory():
    """Test orchestrator with conversation history for follow-up questions."""
    setup_logger()
    
    orchestrator = get_orchestrator()
    
    logger.info("🧠 Testing Conversation Memory\n")
    logger.info("="*70)
    
    # Simulate a conversation with follow-ups
    conversation_history = []
    
    # Query 1: Initial question about points
    logger.info("\n📝 Query 1: Initial question")
    logger.info("-" * 70)
    query1 = "How many points does 1st place get?"
    logger.info(f"User: {query1}")
    
    result1 = orchestrator.process_query(query1, conversation_history=conversation_history)
    response1 = result1.get('content', '')
    logger.info(f"Assistant: {response1}")
    logger.info(f"Tools used: {result1.get('tools_used', [])}")
    
    # Update conversation history
    conversation_history.append({"role": "user", "content": query1})
    conversation_history.append({"role": "assistant", "content": response1})
    
    # Query 2: Follow-up WITHOUT context (should fail or be confused)
    logger.info("\n📝 Query 2: Follow-up question (WITH memory)")
    logger.info("-" * 70)
    query2 = "What about 2nd place?"
    logger.info(f"User: {query2}")
    logger.info(f"Conversation history: {len(conversation_history)} messages")
    
    result2 = orchestrator.process_query(query2, conversation_history=conversation_history)
    response2 = result2.get('content', '')
    logger.info(f"Assistant: {response2}")
    logger.info(f"Tools used: {result2.get('tools_used', [])}")
    
    # Update conversation history
    conversation_history.append({"role": "user", "content": query2})
    conversation_history.append({"role": "assistant", "content": response2})
    
    # Query 3: Another follow-up
    logger.info("\n📝 Query 3: Another follow-up (WITH memory)")
    logger.info("-" * 70)
    query3 = "And 3rd?"
    logger.info(f"User: {query3}")
    logger.info(f"Conversation history: {len(conversation_history)} messages")
    
    result3 = orchestrator.process_query(query3, conversation_history=conversation_history)
    response3 = result3.get('content', '')
    logger.info(f"Assistant: {response3}")
    logger.info(f"Tools used: {result3.get('tools_used', [])}")
    
    # Update conversation history
    conversation_history.append({"role": "user", "content": query3})
    conversation_history.append({"role": "assistant", "content": response3})
    
    # Query 4: Switch topic (should handle context switch)
    logger.info("\n📝 Query 4: Topic switch (memory persists)")
    logger.info("-" * 70)
    query4 = "Show me Monaco circuit"
    logger.info(f"User: {query4}")
    logger.info(f"Conversation history: {len(conversation_history)} messages")
    
    result4 = orchestrator.process_query(query4, conversation_history=conversation_history)
    response4 = result4.get('content', '')
    logger.info(f"Assistant: {response4}")
    logger.info(f"Tools used: {result4.get('tools_used', [])}")
    
    # Update conversation history
    conversation_history.append({"role": "user", "content": query4})
    conversation_history.append({"role": "assistant", "content": response4})
    
    # Query 5: Follow-up about circuit (should remember Monaco)
    logger.info("\n📝 Query 5: Follow-up about previous circuit")
    logger.info("-" * 70)
    query5 = "What are the rules there?"
    logger.info(f"User: {query5}")
    logger.info(f"Conversation history: {len(conversation_history)} messages")
    
    result5 = orchestrator.process_query(query5, conversation_history=conversation_history)
    response5 = result5.get('content', '')
    logger.info(f"Assistant: {response5}")
    logger.info(f"Tools used: {result5.get('tools_used', [])}")
    
    # Summary
    logger.info("\n" + "="*70)
    logger.info("✅ CONVERSATION MEMORY TEST COMPLETE")
    logger.info("="*70)
    logger.info(f"\nTotal queries: 5")
    logger.info(f"Conversation history length: {len(conversation_history)} messages")
    logger.info(f"Exchanges: {len(conversation_history) // 2}")
    
    logger.info("\n📊 Expected Behavior:")
    logger.info("  ✓ Query 2 should understand '2nd place' refers to points")
    logger.info("  ✓ Query 3 should understand '3rd' also refers to points")
    logger.info("  ✓ Query 5 should understand 'there' refers to Monaco")
    
    logger.info("\n🧠 Memory helps with:")
    logger.info("  • Follow-up questions without repeating context")
    logger.info("  • Pronoun resolution ('it', 'there', 'that')")
    logger.info("  • Topic continuity across multiple turns")
    logger.info("  • Natural conversation flow")


def test_without_memory():
    """Test the same queries WITHOUT conversation history."""
    logger.info("\n\n" + "="*70)
    logger.info("🚫 Testing WITHOUT Conversation Memory (for comparison)")
    logger.info("="*70)
    
    orchestrator = get_orchestrator()
    
    # Query 2 without context (should be confused)
    logger.info("\n📝 Follow-up WITHOUT memory")
    logger.info("-" * 70)
    query = "What about 2nd place?"
    logger.info(f"User: {query}")
    logger.info("Conversation history: NONE (empty)")
    
    result = orchestrator.process_query(query, conversation_history=[])
    response = result.get('content', '')
    logger.info(f"Assistant: {response}")
    logger.info(f"Tools used: {result.get('tools_used', [])}")
    
    logger.info("\n⚠️  Without memory, agent cannot understand '2nd place' context")
    logger.info("   It doesn't know we were talking about points!")


if __name__ == "__main__":
    test_conversation_memory()
    test_without_memory()
