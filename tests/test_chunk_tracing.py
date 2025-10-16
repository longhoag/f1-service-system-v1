"""
Test script to demonstrate chunk retrieval tracing.
Shows what chunks Bedrock retrieves before generation.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from loguru import logger
from src.agents.orchestrator import get_orchestrator


def display_chunks(result: dict):
    """Display retrieved chunks in a readable format."""
    metadata = result.get('metadata', {})
    chunks = metadata.get('retrieved_chunks', [])
    
    if not chunks:
        print("   ⚠️  No chunks found in metadata")
        return
    
    print(f"\n   📦 Retrieved {len(chunks)} chunks (sorted by relevance):\n")
    
    for idx, chunk in enumerate(chunks, 1):
        score = chunk.get('score', 0.0)
        source = chunk.get('source', 'Unknown')
        text = chunk.get('text', '')
        char_count = chunk.get('char_count', 0)
        
        # Display chunk header
        print(f"   Chunk {idx}:")
        print(f"   ├─ Relevance Score: {score:.4f}")
        print(f"   ├─ Source: {source}")
        print(f"   ├─ Length: {char_count} characters")
        print(f"   └─ Content Preview:")
        
        # Display first 200 chars with line wrapping
        preview = text[:300].replace('\n', ' ')
        if len(text) > 300:
            preview += "..."
        
        # Wrap text at 80 chars
        words = preview.split()
        line = "      "
        for word in words:
            if len(line) + len(word) + 1 > 80:
                print(line)
                line = "      " + word + " "
            else:
                line += word + " "
        if line.strip():
            print(line)
        
        print()


def main():
    """Run test queries and display retrieved chunks."""
    print("=" * 80)
    print("F1 AGENT CHUNK RETRIEVAL TRACING TEST")
    print("=" * 80)
    print()
    
    # Initialize orchestrator
    print("Initializing orchestrator...")
    orchestrator = get_orchestrator()
    print("✓ Orchestrator ready\n")
    
    # Test queries
    test_queries = [
        {
            "query": "How many points for 1st position?",
            "description": "Points system query (factual)"
        },
        {
            "query": "Explain the safety car procedure",
            "description": "Safety car procedure (explanatory)"
        },
        {
            "query": "What's the penalty for a false start?",
            "description": "Penalty query (specific)"
        }
    ]
    
    for idx, test in enumerate(test_queries, 1):
        query = test['query']
        description = test['description']
        
        print("=" * 80)
        print(f"TEST {idx}/3: {description}")
        print("=" * 80)
        print(f"Query: '{query}'")
        print()
        
        try:
            # Process query
            result = orchestrator.process_query(query)
            
            # Display intent and response type
            print(f"Intent: {result.get('intent', 'unknown')}")
            print(f"Response type: {result['response']['type']}")
            
            # Display chunks if available
            if result['response']['type'] == 'text':
                display_chunks(result['response'])
                
                # Display generated answer
                answer = result['response']['content']
                print(f"   📝 Generated Answer ({len(answer)} chars):")
                print(f"   {'-' * 70}")
                # Show first 300 chars
                preview = answer[:300]
                if len(answer) > 300:
                    preview += "..."
                for line in preview.split('\n'):
                    print(f"   {line}")
                print()
                
            elif result['response']['type'] == 'combined':
                # For combined responses, show regulations chunks
                regs_result = result.get('regulations_result', {})
                if regs_result:
                    display_chunks(regs_result)
            
            # Display sources
            sources = result['response'].get('metadata', {}).get('sources', [])
            if sources:
                print(f"   📚 Sources: {', '.join(sources)}")
            
            print()
            
        except Exception as e:
            logger.error(f"Query failed: {e}")
            print(f"   ❌ ERROR: {e}\n")
    
    print("=" * 80)
    print("TRACING INFORMATION")
    print("=" * 80)
    print()
    print("Check your LangSmith dashboard for detailed traces:")
    print("https://smith.langchain.com/")
    print()
    print("Traces will show:")
    print("  • extract_chunks - Retrieved chunks with scores")
    print("  • retrieve_and_generate - Full Bedrock API call")
    print("  • query_regulations - Complete RAG flow")
    print()
    print("Each chunk's relevance score indicates how well it matches the query.")
    print("Higher scores (closer to 1.0) mean better semantic match.")
    print()


if __name__ == "__main__":
    main()
