"""
Multi-Model Latency Comparison Test
Compares: GPT-5 Mini, GPT-5 Nano, GPT-4o, GPT-4o-mini, Bedrock Claude
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import time
from openai import OpenAI
import boto3
from loguru import logger
from src.config.settings import settings


def test_bedrock_retrieve(query: str, num_results: int = 5):
    """Test Bedrock retrieval speed."""
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


def test_openai_generation(model: str, query: str, chunks: list):
    """Test OpenAI generation speed for a specific model."""
    client = OpenAI(api_key=settings.openai_api_key)
    
    # Build context
    context_parts = []
    for idx, chunk in enumerate(chunks, 1):
        context_parts.append(f"[Chunk {idx} - Score: {chunk['score']:.4f}]\n{chunk['text']}\n")
    context = "\n".join(context_parts)
    
    # GPT-5 and o1 models have different requirements
    is_gpt5 = model.startswith('gpt-5')
    is_o1 = model.startswith('o1')
    
    # Build messages based on model type
    if is_o1 or is_gpt5:
        # o1 and GPT-5 models don't support system messages
        user_prompt = f"""You are an expert F1 regulations assistant. Answer based on the provided chunks.

Question: {query}

Regulation chunks:
{context}

Provide a clear answer:"""
        messages = [{"role": "user", "content": user_prompt}]
    else:
        # GPT-4o models support system messages
        system_prompt = """You are an expert F1 regulations assistant. Answer based on the provided chunks."""
        user_prompt = f"""Question: {query}

Regulation chunks:
{context}

Provide a clear answer:"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    
    # Build request parameters
    request_params = {
        "model": model,
        "messages": messages
    }
    
    # Add parameters only if model supports them
    if not is_gpt5:
        # GPT-5 models don't support max_tokens, temperature
        request_params["max_tokens"] = settings.openai_max_tokens
        request_params["temperature"] = settings.openai_temperature
    
    start = time.time()
    response = client.chat.completions.create(**request_params)
    elapsed = time.time() - start
    
    answer = response.choices[0].message.content
    tokens = response.usage.total_tokens
    
    return answer, tokens, elapsed


def test_bedrock_retrieve_and_generate(query: str):
    """Test Bedrock RetrieveAndGenerate (single call)."""
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
    return answer, elapsed


def main():
    """Run comprehensive latency comparison."""
    print("=" * 100)
    print("MULTI-MODEL LATENCY COMPARISON TEST")
    print("=" * 100)
    print()
    print("Testing Models:")
    print("  1. GPT-5 Mini (Bedrock Retrieve + OpenAI Generate) - NEWEST")
    print("  2. GPT-5 Nano (Bedrock Retrieve + OpenAI Generate) - NEWEST")
    print("  3. GPT-4o-mini (Bedrock Retrieve + OpenAI Generate)")
    print("  4. GPT-4o (Bedrock Retrieve + OpenAI Generate)")
    print("  5. Bedrock Claude 3 Sonnet (RetrieveAndGenerate - Baseline)")
    print()
    print("=" * 100)
    print()
    
    # Test queries
    test_queries = [
        "How many points for 1st position?",
        "Explain the safety car procedure",
        "What's the penalty for a false start?"
    ]
    
    # Models to test (ordered by newest/fastest first)
    openai_models = [
        ("gpt-5-mini", "GPT-5 Mini"),
        ("gpt-5-nano", "GPT-5 Nano"),
        ("gpt-4o-mini", "GPT-4o-mini"),
        ("gpt-4o", "GPT-4o")
    ]
    
    results = {}
    
    for query in test_queries:
        print(f"Query: '{query}'")
        print("-" * 100)
        
        # First, retrieve chunks (same for all OpenAI models)
        print("  📥 Bedrock Retrieve...", end=" ", flush=True)
        chunks, retrieve_time = test_bedrock_retrieve(query)
        print(f"✓ {retrieve_time:.2f}s ({len(chunks)} chunks)")
        
        # Test each OpenAI model
        for model_id, model_name in openai_models:
            print(f"  🤖 {model_name} Generate...", end=" ", flush=True)
            try:
                answer, tokens, gen_time = test_openai_generation(model_id, query, chunks)
                total_time = retrieve_time + gen_time
                
                # Store results
                if model_name not in results:
                    results[model_name] = []
                results[model_name].append({
                    "query": query,
                    "retrieve_time": retrieve_time,
                    "generate_time": gen_time,
                    "total_time": total_time,
                    "tokens": tokens,
                    "answer_length": len(answer)
                })
                
                print(f"✓ {gen_time:.2f}s (Total: {total_time:.2f}s, {tokens} tokens, {len(answer)} chars)")
            except Exception as e:
                print(f"❌ ERROR: {e}")
                if model_name not in results:
                    results[model_name] = []
                results[model_name].append({
                    "query": query,
                    "error": str(e)
                })
        
        # Test Bedrock baseline
        print(f"  🔷 Bedrock Claude 3 Sonnet (RetrieveAndGenerate)...", end=" ", flush=True)
        try:
            answer, total_time = test_bedrock_retrieve_and_generate(query)
            
            if "Bedrock Claude" not in results:
                results["Bedrock Claude"] = []
            results["Bedrock Claude"].append({
                "query": query,
                "total_time": total_time,
                "answer_length": len(answer)
            })
            
            print(f"✓ {total_time:.2f}s ({len(answer)} chars)")
        except Exception as e:
            print(f"❌ ERROR: {e}")
        
        print()
    
    # Summary
    print("=" * 100)
    print("PERFORMANCE SUMMARY")
    print("=" * 100)
    print()
    
    for model_name in results:
        model_results = results[model_name]
        successful = [r for r in model_results if "error" not in r]
        
        if not successful:
            print(f"❌ {model_name}: All queries failed")
            continue
        
        avg_total = sum(r['total_time'] for r in successful) / len(successful)
        
        if "retrieve_time" in successful[0]:
            avg_retrieve = sum(r['retrieve_time'] for r in successful) / len(successful)
            avg_generate = sum(r['generate_time'] for r in successful) / len(successful)
            avg_tokens = sum(r['tokens'] for r in successful) / len(successful)
            
            print(f"🤖 {model_name}:")
            print(f"   ├─ Avg Total Time: {avg_total:.2f}s")
            print(f"   ├─ Avg Retrieve Time: {avg_retrieve:.2f}s")
            print(f"   ├─ Avg Generate Time: {avg_generate:.2f}s")
            print(f"   └─ Avg Tokens: {avg_tokens:.0f}")
        else:
            print(f"🔷 {model_name}:")
            print(f"   └─ Avg Total Time: {avg_total:.2f}s")
        print()
    
    # Ranking
    print("=" * 100)
    print("⚡ SPEED RANKING (Fastest to Slowest)")
    print("=" * 100)
    print()
    
    avg_times = []
    for model_name in results:
        successful = [r for r in results[model_name] if "error" not in r]
        if successful:
            avg_total = sum(r['total_time'] for r in successful) / len(successful)
            avg_times.append((model_name, avg_total))
    
    avg_times.sort(key=lambda x: x[1])
    
    for rank, (model_name, avg_time) in enumerate(avg_times, 1):
        speedup = avg_times[-1][1] / avg_time if avg_time > 0 else 0
        print(f"  {rank}. {model_name}: {avg_time:.2f}s (baseline) - {speedup:.2f}x faster than slowest")
    
    print()
    print("=" * 100)
    print("RECOMMENDATION")
    print("=" * 100)
    print()
    
    if avg_times:
        fastest = avg_times[0]
        print(f"🏆 Fastest Model: {fastest[0]} ({fastest[1]:.2f}s average)")
        print()
        print("Use for:")
        print("  • Production deployments requiring low latency")
        print("  • High-volume query scenarios")
        print("  • Cost-sensitive applications")
    
    print()


if __name__ == "__main__":
    main()
