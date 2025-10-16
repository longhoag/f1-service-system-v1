"""
Latency comparison test: Bedrock Retrieve + OpenAI Generate
Shows retrieved chunks and measures performance tradeoff.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from loguru import logger
from src.agents.orchestrator import get_orchestrator


def display_chunks(chunks: list, max_display: int = 3):
    """Display retrieved chunks in a readable format."""
    if not chunks:
        print("   ⚠️  No chunks retrieved")
        return
    
    print(f"\n   📦 Retrieved {len(chunks)} chunks (showing top {min(max_display, len(chunks))}):\n")
    
    for idx, chunk in enumerate(chunks[:max_display], 1):
        score = chunk.get('score', 0.0)
        source = chunk.get('source', 'Unknown')
        text = chunk.get('text', '')
        char_count = chunk.get('char_count', 0)
        
        print(f"   Chunk {idx}:")
        print(f"   ├─ Relevance Score: {score:.4f}")
        print(f"   ├─ Source: {source}")
        print(f"   ├─ Length: {char_count} characters")
        print(f"   └─ Preview: {text[:150]}...")
        print()


def main():
    """Run latency comparison test."""
    print("=" * 80)
    print("LATENCY COMPARISON: Bedrock Retrieve + OpenAI Generate")
    print("=" * 80)
    print()
    print("Architecture:")
    print("  • Step 1: Bedrock Knowledge Base - Retrieve chunks")
    print("  • Step 2: OpenAI GPT-4o - Generate answer from chunks")
    print()
    print("Benefits:")
    print("  ✓ See exactly which chunks were retrieved (full visibility)")
    print("  ✓ Use GPT-4o for generation (latest model)")
    print("  ✓ Full control over prompt engineering")
    print()
    print("Tradeoffs:")
    print("  • 2 API calls instead of 1 (Bedrock Retrieve + OpenAI Generate)")
    print("  • Higher latency (measured below)")
    print("  • Higher cost (both Bedrock + OpenAI)")
    print()
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
            "description": "Points system (factual)"
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
            
            if result['response']['type'] in ['text', 'combined']:
                # Get metadata
                if result['response']['type'] == 'text':
                    metadata = result['response'].get('metadata', {})
                else:
                    regs_result = result.get('regulations_result', {})
                    metadata = regs_result.get('metadata', {})
                
                # Display timing breakdown
                total_time = metadata.get('total_time', 0)
                retrieval_time = metadata.get('retrieval_time', 0)
                
                print(f"⏱️  TIMING BREAKDOWN:")
                print(f"   ├─ Total time: {total_time:.2f}s")
                print(f"   ├─ Bedrock Retrieve: ~{total_time - retrieval_time:.2f}s")
                print(f"   └─ OpenAI Generate: {retrieval_time:.2f}s")
                print()
                
                # Display chunks
                chunks = metadata.get('chunks', [])
                display_chunks(chunks, max_display=2)
                
                # Display token usage
                tokens_used = metadata.get('tokens_used', 0)
                tokens_prompt = metadata.get('tokens_prompt', 0)
                tokens_completion = metadata.get('tokens_completion', 0)
                
                print(f"   📊 OpenAI Token Usage:")
                print(f"   ├─ Prompt tokens: {tokens_prompt}")
                print(f"   ├─ Completion tokens: {tokens_completion}")
                print(f"   └─ Total tokens: {tokens_used}")
                print()
                
                # Display answer preview
                answer = result['response']['content']
                print(f"   📝 Generated Answer ({len(answer)} chars):")
                preview = answer[:200]
                if len(answer) > 200:
                    preview += "..."
                print(f"   {preview}")
                print()
                
                # Display sources
                sources = metadata.get('sources', [])
                if sources:
                    print(f"   📚 Sources: {', '.join(sources)}")
                print()
            
        except Exception as e:
            logger.error(f"Query failed: {e}")
            print(f"   ❌ ERROR: {e}\n")
    
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    print("✅ New Architecture Benefits:")
    print("  • Full visibility into retrieved chunks with relevance scores")
    print("  • Using GPT-4o (most capable OpenAI model)")
    print("  • Custom prompt engineering possible")
    print("  • All data traced to LangSmith for observability")
    print()
    print("📈 Latency Analysis:")
    print("  • Expected: 2-4s for Bedrock Retrieve + 2-4s for OpenAI Generate")
    print("  • Total: ~4-8s (vs ~4-6s for single RetrieveAndGenerate call)")
    print("  • Tradeoff: +0-4s latency for full chunk visibility")
    print()
    print("🔍 LangSmith Tracing:")
    print("  https://smith.langchain.com/")
    print("  Project: f1-service-system-v1")
    print()
    print("  Traces now show:")
    print("    1. retrieve_chunks - Full chunk details with scores")
    print("    2. generate_with_openai - GPT-4o generation with token usage")
    print()


if __name__ == "__main__":
    main()
