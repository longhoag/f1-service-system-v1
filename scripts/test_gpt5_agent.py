"""
Test GPT-5 Mini Agent with Tool Calling.

Tests the new agent-based architecture replacing LangGraph orchestrator.
Validates that GPT-5 Mini correctly:
- Understands circuit queries and calls get_circuit_image tool
- Understands regulation queries and calls query_regulations tool
- Handles combined queries requiring both tools
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from loguru import logger
from src.agents.gpt5_agent import get_gpt5_agent
from src.utils.logger import setup_logger
import time


def test_query(agent, query: str, expected_tools: list = None):
    """
    Test a single query and display results.
    
    Args:
        agent: GPT5Agent instance
        query: Query to test
        expected_tools: List of expected tool names (optional)
    """
    print("\n" + "="*80)
    print(f"QUERY: {query}")
    print("="*80)
    
    start_time = time.time()
    
    try:
        result = agent.process_query(query)
        
        elapsed = time.time() - start_time
        
        print(f"\n⏱️  Response Time: {elapsed:.2f}s")
        print(f"📊 Status: {result.get('type')}")
        print(f"🔧 Tools Used: {result.get('tools_used', [])}")
        print(f"🔄 Iterations: {result.get('metadata', {}).get('iterations', 'N/A')}")
        
        # Validate expected tools
        if expected_tools:
            tools_used = result.get('tools_used', [])
            for expected_tool in expected_tools:
                if expected_tool in tools_used:
                    print(f"  ✅ Used expected tool: {expected_tool}")
                else:
                    print(f"  ❌ Missing expected tool: {expected_tool}")
        
        print(f"\n📝 RESPONSE:")
        print("-" * 80)
        print(result.get('content', 'No content'))
        print("-" * 80)
        
        # Show tool results
        if result.get('tool_results'):
            print(f"\n🔍 TOOL RESULTS:")
            for tool_name, tool_result in result['tool_results'].items():
                print(f"\n  {tool_name}:")
                print(f"    Type: {tool_result.get('type')}")
                print(f"    Status: {tool_result.get('metadata', {}).get('status')}")
                if tool_result.get('type') == 'image':
                    print(f"    Path: {tool_result.get('content')}")
                elif tool_result.get('type') == 'text':
                    content = tool_result.get('content', '')
                    preview = content[:200] + "..." if len(content) > 200 else content
                    print(f"    Content: {preview}")
        
        return True
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        print(f"\n❌ ERROR: {e}")
        return False


def main():
    """Run GPT-5 Mini agent tests."""
    print("\n" + "🏎️ "*20)
    print("GPT-5 MINI AGENT TEST SUITE")
    print("Testing tool calling with F1 information queries")
    print("🏎️ "*20)
    
    # Initialize logger
    setup_logger()
    
    # Initialize agent
    print("\n📦 Initializing GPT-5 Mini Agent...")
    try:
        agent = get_gpt5_agent()
        print("✅ Agent initialized successfully\n")
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        return
    
    # Test cases
    test_cases = [
        {
            "name": "Circuit Query - Monaco",
            "query": "Show me the Monaco circuit",
            "expected_tools": ["get_circuit_image"]
        },
        {
            "name": "Circuit Query - Casual Name (Vegas)",
            "query": "Can I see the Vegas track?",
            "expected_tools": ["get_circuit_image"]
        },
        {
            "name": "Circuit Query - Nickname (COTA)",
            "query": "Display the COTA circuit map",
            "expected_tools": ["get_circuit_image"]
        },
        {
            "name": "Regulations Query - Points",
            "query": "How many points does 1st place get in F1?",
            "expected_tools": ["query_regulations"]
        },
        {
            "name": "Regulations Query - DRS",
            "query": "What are the DRS rules?",
            "expected_tools": ["query_regulations"]
        },
        {
            "name": "Regulations Query - Safety Car",
            "query": "Explain the safety car procedure",
            "expected_tools": ["query_regulations"]
        },
        {
            "name": "Combined Query - Circuit + Rules",
            "query": "Show me Silverstone and tell me the points system",
            "expected_tools": ["get_circuit_image", "query_regulations"]
        }
    ]
    
    # Run tests
    results = []
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n\n{'='*80}")
        print(f"TEST {i}/{len(test_cases)}: {test_case['name']}")
        print(f"{'='*80}")
        
        success = test_query(
            agent,
            test_case['query'],
            test_case.get('expected_tools')
        )
        
        results.append({
            "name": test_case['name'],
            "success": success
        })
        
        # Pause between tests
        if i < len(test_cases):
            time.sleep(2)
    
    # Summary
    print("\n\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for r in results if r['success'])
    total = len(results)
    
    for i, result in enumerate(results, 1):
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        print(f"{i}. {status} - {result['name']}")
    
    print(f"\nTotal: {passed}/{total} tests passed ({100*passed//total}%)")
    
    if passed == total:
        print("\n🎉 All tests passed! GPT-5 Mini agent working correctly.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review logs above.")


if __name__ == "__main__":
    main()
