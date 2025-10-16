"""
Side-by-Side Comparison: Bedrock RetrieveAndGenerate vs Bedrock Retrieve + GPT-4o
Compare both latency and output quality for accuracy inspection.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import time
import boto3
from openai import OpenAI
from loguru import logger
from src.config.settings import settings


def bedrock_retrieve_chunks(query: str, num_results: int = 5):
    """Retrieve chunks from Bedrock Knowledge Base."""
    bedrock_agent = boto3.client(
        'bedrock-agent-runtime',
        region_name=settings.aws_region,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key
    )
    
    start = time.time()
    response = bedrock_agent.retrieve(
        knowledgeBaseId=settings.bedrock_kb_id,
        retrievalQuery={"text": query},
        retrievalConfiguration={
            "vectorSearchConfiguration": {
                "numberOfResults": num_results,
                "overrideSearchType": "SEMANTIC"
            }
        }
    )
    elapsed = time.time() - start
    
    # Extract chunks
    chunks = []
    for result in response.get('retrievalResults', []):
        content = result.get('content', {})
        text = content.get('text', '') if isinstance(content, dict) else str(content)
        if text and len(text.strip()) > 0:
            chunks.append({
                "text": text,
                "score": result.get('score', 0.0),
                "char_count": len(text)
            })
    
    return chunks, elapsed


def gpt4o_generate(query: str, chunks: list):
    """Generate answer using GPT-4o."""
    client = OpenAI(api_key=settings.openai_api_key)
    
    # Build context
    context_parts = []
    for idx, chunk in enumerate(chunks, 1):
        context_parts.append(
            f"[Chunk {idx} - Relevance: {chunk['score']:.4f}]\n{chunk['text']}\n"
        )
    context = "\n".join(context_parts)
    
    system_prompt = """You are an expert F1 regulations assistant with deep knowledge of FIA Formula 1 rules.

Answer the question based ONLY on the provided regulation chunks.
Be precise, cite article numbers when available, and explain technical terms clearly.
If the information is not in the provided chunks, clearly state that.
Provide a clear, well-structured answer."""

    user_prompt = f"""Question: {query}

Regulation chunks:
{context}

Provide a clear, well-structured answer:"""
    
    start = time.time()
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        max_tokens=1500,
        temperature=0.3
    )
    elapsed = time.time() - start
    
    answer = response.choices[0].message.content
    tokens = response.usage.total_tokens
    
    return answer, tokens, elapsed


def bedrock_retrieve_and_generate(query: str):
    """Use Bedrock RetrieveAndGenerate (single call)."""
    bedrock_agent = boto3.client(
        'bedrock-agent-runtime',
        region_name=settings.aws_region,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key
    )
    
    start = time.time()
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
                            "maxTokens": 1500,
                            "temperature": 0.3
                        }
                    },
                    "promptTemplate": {
                        "textPromptTemplate": """You are an expert F1 regulations assistant with deep knowledge of FIA Formula 1 rules.

Answer the question based ONLY on the provided regulation chunks.
Be precise, cite article numbers when available, and explain technical terms clearly.
If the information is not in the provided chunks, clearly state that.

Question: $query$

Regulation chunks: $search_results$

Provide a clear, well-structured answer:"""
                    }
                },
                "retrievalConfiguration": {
                    "vectorSearchConfiguration": {
                        "numberOfResults": 5,
                        "overrideSearchType": "SEMANTIC"
                    }
                }
            }
        }
    )
    elapsed = time.time() - start
    
    answer = response.get('output', {}).get('text', '')
    citations = response.get('citations', [])
    
    # Extract sources
    sources = []
    for citation in citations:
        for ref in citation.get('retrievedReferences', []):
            location = ref.get('location', {})
            source_uri = location.get('s3Location', {}).get('uri', '')
            if source_uri:
                filename = source_uri.split('/')[-1] if '/' in source_uri else source_uri
                if filename not in sources:
                    sources.append(filename)
    
    return answer, sources, elapsed


def display_chunks(chunks: list):
    """Display retrieved chunks."""
    print(f"\n   📦 Retrieved Chunks ({len(chunks)} total):\n")
    for idx, chunk in enumerate(chunks, 1):
        score = chunk.get('score', 0.0)
        text = chunk.get('text', '')
        char_count = chunk.get('char_count', 0)
        
        print(f"   Chunk {idx}:")
        print(f"   ├─ Relevance Score: {score:.4f}")
        print(f"   ├─ Length: {char_count} characters")
        print(f"   └─ Content:")
        
        # Show full content (wrapped at 100 chars)
        lines = text.split('\n')
        for line in lines[:10]:  # Show first 10 lines
            if len(line) > 100:
                # Wrap long lines
                for i in range(0, len(line), 100):
                    print(f"      {line[i:i+100]}")
            else:
                print(f"      {line}")
        
        if len(lines) > 10:
            print(f"      ... ({len(lines) - 10} more lines)")
        print()


def display_answer(title: str, answer: str, extra_info: str = ""):
    """Display generated answer."""
    print(f"\n   📝 {title}:")
    print(f"   {'=' * 90}")
    
    # Show full answer
    lines = answer.split('\n')
    for line in lines:
        if len(line) > 100:
            # Wrap long lines
            for i in range(0, len(line), 100):
                print(f"   {line[i:i+100]}")
        else:
            print(f"   {line}")
    
    print(f"   {'=' * 90}")
    print(f"   Length: {len(answer)} characters")
    if extra_info:
        print(f"   {extra_info}")
    print()


def compare_answers(bedrock_answer: str, gpt4o_answer: str):
    """Compare answer characteristics."""
    print("\n   📊 Answer Comparison:")
    print(f"   ├─ Bedrock Claude Length: {len(bedrock_answer)} chars")
    print(f"   ├─ GPT-4o Length: {len(gpt4o_answer)} chars")
    print(f"   └─ Difference: {abs(len(bedrock_answer) - len(gpt4o_answer))} chars")
    
    # Check for key differences
    bedrock_lines = len(bedrock_answer.split('\n'))
    gpt4o_lines = len(gpt4o_answer.split('\n'))
    print(f"\n   ├─ Bedrock Claude Lines: {bedrock_lines}")
    print(f"   ├─ GPT-4o Lines: {gpt4o_lines}")
    print(f"   └─ Structure Difference: {abs(bedrock_lines - gpt4o_lines)} lines")


def main():
    """Run side-by-side comparison."""
    print("=" * 100)
    print("SIDE-BY-SIDE COMPARISON: Bedrock RetrieveAndGenerate vs Bedrock Retrieve + GPT-4o")
    print("=" * 100)
    print()
    print("Architecture 1: Bedrock RetrieveAndGenerate (Single Call)")
    print("  • Single API call to Bedrock")
    print("  • Claude 3 Sonnet generates answer")
    print("  • No chunk visibility")
    print()
    print("Architecture 2: Bedrock Retrieve + GPT-4o Generate (Two Calls)")
    print("  • Step 1: Bedrock retrieves chunks")
    print("  • Step 2: GPT-4o generates answer from chunks")
    print("  • Full chunk visibility")
    print()
    print("=" * 100)
    print()
    
    # Test queries
    test_queries = [
        {
            "query": "How many points for 1st position in both a regular race and a sprint?",
            "description": "Points system (factual, multi-part)"
        },
        {
            "query": "Explain the complete safety car procedure including when it's deployed and driver requirements",
            "description": "Safety car procedure (explanatory, detailed)"
        },
        {
            "query": "What are the specific penalties for a false start?",
            "description": "Penalty query (specific regulation)"
        }
    ]
    
    for idx, test in enumerate(test_queries, 1):
        query = test['query']
        description = test['description']
        
        print("=" * 100)
        print(f"TEST {idx}/3: {description}")
        print("=" * 100)
        print(f"Query: '{query}'")
        print()
        
        # ========================================
        # Method 1: Bedrock RetrieveAndGenerate
        # ========================================
        print("─" * 100)
        print("METHOD 1: Bedrock RetrieveAndGenerate (Single Call)")
        print("─" * 100)
        
        try:
            bedrock_answer, sources, bedrock_time = bedrock_retrieve_and_generate(query)
            
            print(f"   ⏱️  Total Time: {bedrock_time:.2f}s")
            print(f"   📚 Sources: {', '.join(sources) if sources else 'None'}")
            
            display_answer(
                "Bedrock Claude 3 Sonnet Answer",
                bedrock_answer
            )
            
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            bedrock_answer = None
            bedrock_time = 0
        
        # ========================================
        # Method 2: Bedrock Retrieve + GPT-4o
        # ========================================
        print("─" * 100)
        print("METHOD 2: Bedrock Retrieve + GPT-4o Generate (Two Calls)")
        print("─" * 100)
        
        try:
            # Step 1: Retrieve
            print("   Step 1: Bedrock Retrieve...")
            chunks, retrieve_time = bedrock_retrieve_chunks(query)
            print(f"   ⏱️  Retrieve Time: {retrieve_time:.2f}s")
            
            # Display chunks
            display_chunks(chunks)
            
            # Step 2: Generate
            print("   Step 2: GPT-4o Generate...")
            gpt4o_answer, tokens, generate_time = gpt4o_generate(query, chunks)
            print(f"   ⏱️  Generate Time: {generate_time:.2f}s")
            print(f"   🎯 Total Time: {retrieve_time + generate_time:.2f}s")
            print(f"   🔢 Tokens Used: {tokens}")
            
            display_answer(
                "GPT-4o Answer",
                gpt4o_answer,
                f"Tokens: {tokens}"
            )
            
            gpt4o_total_time = retrieve_time + generate_time
            
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            gpt4o_answer = None
            gpt4o_total_time = 0
        
        # ========================================
        # Comparison
        # ========================================
        if bedrock_answer and gpt4o_answer:
            print("─" * 100)
            print("COMPARISON")
            print("─" * 100)
            
            print(f"\n   ⏱️  Latency:")
            print(f"   ├─ Bedrock RetrieveAndGenerate: {bedrock_time:.2f}s")
            print(f"   ├─ Bedrock Retrieve + GPT-4o: {gpt4o_total_time:.2f}s")
            
            diff = gpt4o_total_time - bedrock_time
            percent_diff = (diff / bedrock_time) * 100
            
            if diff > 0:
                print(f"   └─ GPT-4o is {diff:.2f}s SLOWER ({percent_diff:+.1f}%)")
            else:
                print(f"   └─ GPT-4o is {abs(diff):.2f}s FASTER ({percent_diff:+.1f}%)")
            
            compare_answers(bedrock_answer, gpt4o_answer)
            
            print("\n   🎯 Accuracy Assessment:")
            print("   └─ Review both answers above to compare:")
            print("      • Correctness of information")
            print("      • Completeness of answer")
            print("      • Clarity and structure")
            print("      • Citation of article numbers")
        
        print()
    
    print("=" * 100)
    print("SUMMARY")
    print("=" * 100)
    print()
    print("Review the answers above to determine:")
    print("  1. Which model provides more accurate information?")
    print("  2. Which model structures answers better?")
    print("  3. Which model cites regulations more precisely?")
    print("  4. Is the latency tradeoff worth the quality difference?")
    print()
    print("Key Observations:")
    print("  • Bedrock: Single call, no chunk visibility, Claude 3 Sonnet")
    print("  • GPT-4o: Two calls, full chunk visibility, latest OpenAI model")
    print()


if __name__ == "__main__":
    main()
