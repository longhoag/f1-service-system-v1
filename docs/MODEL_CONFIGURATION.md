# Bedrock Model Configuration

## Current Model Setup

### Generation Model: Claude 3 Sonnet
**Model ID**: `anthropic.claude-3-sonnet-20240229-v1:0`

**Why Claude 3 Sonnet (not 3.5)?**
- Claude 3.5 Sonnet v2 (`anthropic.claude-3-5-sonnet-20241022-v2:0`) requires **inference profiles** for RetrieveAndGenerate API
- Inference profiles are NOT supported for on-demand throughput in Knowledge Base integration
- Claude 3 Sonnet v1 provides excellent quality while supporting on-demand access

**Configuration Location**:
- Environment Variable: `.env` → `BEDROCK_GENERATION_MODEL=anthropic.claude-3-sonnet-20240229-v1:0`
- Settings Class: `src/config/settings.py` → `bedrock_generation_model`
- All production code should use: `settings.bedrock_generation_model`

### Embedding Model: Amazon Titan V2
**Model ID**: `amazon.titan-embed-text-v2:0`

**Configuration**:
- Dimensions: 1024
- Used for semantic chunking and vector storage in Bedrock Knowledge Base
- Environment Variable: `BEDROCK_EMBEDDING_MODEL=amazon.titan-embed-text-v2:0`

## Model Performance Results

### Test Results (2025-10-15)

**Success Rate**: 100% (2/2 queries)
**High Quality Rate**: 100% (2/2 queries)
**Average Response Time**: 4.93s

#### Query 1: Financial Regulations Date
- **Query**: "according to financial regulations, when the financial regulations came into force?"
- **Result**: ✅ High quality (100% keyword coverage, 505 chars, 2 citations)
- **Response Time**: 4.40s
- **Sources**: Financial regulations PDF, Power Unit financial regulations PDF
- **Quality**: Comprehensive answer with clear distinction between general and PU regulations

#### Query 2: Points System
- **Query**: "How much points will be awarded for 1st position?"
- **Result**: ✅ High quality (100% keyword coverage, 761 chars, 2 citations)
- **Response Time**: 5.45s
- **Sources**: Sporting regulations PDF
- **Quality**: Detailed breakdown for both normal races and sprint sessions with distance-based variations

## Migration Notes

### What Changed
1. **`.env`**: Updated `BEDROCK_GENERATION_MODEL` from `anthropic.claude-3-5-sonnet-20241022-v2:0` to `anthropic.claude-3-sonnet-20240229-v1:0`
2. **`src/config/settings.py`**: Updated default value for `bedrock_generation_model`
3. **`scripts/test_bedrock_retrieve_and_generate.py`**: Now uses `settings.bedrock_generation_model` instead of hardcoded value
4. **`.github/copilot-instructions.md`**: Added Bedrock Model Configuration section documenting the limitation

### Error Before Fix
```
ValidationException: Invocation of model ID anthropic.claude-3-5-sonnet-20241022-v2:0 
with on-demand throughput isn't supported. Retry your request with the ID or ARN of 
an inference profile that contains this model.
```

### Why This Happened
- AWS Bedrock's `RetrieveAndGenerate` API with Knowledge Base integration uses on-demand throughput
- Claude 3.5 Sonnet v2 requires provisioned throughput via inference profiles
- Inference profiles are not compatible with the Knowledge Base `RetrieveAndGenerate` workflow

## Future Considerations

### When to Use Claude 3.5 Sonnet v2
If you need Claude 3.5 Sonnet's enhanced capabilities, you must:
1. Use **manual retrieval + generation** (not RetrieveAndGenerate)
2. Call `retrieve()` to get chunks
3. Call `invoke_model()` with Claude 3.5 Sonnet inference profile
4. Pass chunks as context in the prompt

Example workflow:
```python
# Step 1: Retrieve chunks
chunks = bedrock_agent.retrieve(
    knowledgeBaseId=kb_id,
    retrievalQuery={"text": query}
)

# Step 2: Build context from chunks
context = "\n".join([chunk['content']['text'] for chunk in chunks['retrievalResults']])

# Step 3: Generate with Claude 3.5 Sonnet via inference profile
response = bedrock_runtime.invoke_model(
    modelId="arn:aws:bedrock:us-east-1:855386719590:inference-profile/us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    body=json.dumps({
        "messages": [{"role": "user", "content": f"Context: {context}\n\nQuestion: {query}"}],
        "max_tokens": 2048,
        "temperature": 0.7
    })
)
```

### Alternative Models Supported
Other models that work with RetrieveAndGenerate on-demand:
- ✅ `anthropic.claude-3-sonnet-20240229-v1:0` (current choice)
- ✅ `anthropic.claude-3-haiku-20240307-v1:0` (faster, lower cost)
- ✅ `anthropic.claude-instant-v1` (legacy, not recommended)
- ✅ Amazon Titan models (lower quality for complex reasoning)

## Quality Assessment

### Claude 3 Sonnet Performance
Based on testing, Claude 3 Sonnet provides:
- ✅ Accurate extraction of regulation details
- ✅ Clear distinction between different regulation types
- ✅ Proper citation of source documents
- ✅ Comprehensive answers with relevant context
- ✅ Honest acknowledgment when information is not available

### Comparison to Claude 3.5 Sonnet v2
While we cannot use Claude 3.5 Sonnet v2 directly in RetrieveAndGenerate:
- Claude 3 Sonnet is sufficient for F1 regulation queries (factual retrieval)
- Claude 3.5 Sonnet v2 would provide marginal benefits for this use case
- The convenience of RetrieveAndGenerate API outweighs the slight quality difference

## Recommendations

1. **Keep Claude 3 Sonnet** for production RAG pipeline
2. **Monitor AWS announcements** for inference profile support in RetrieveAndGenerate
3. **Consider manual pipeline** only if quality issues arise (none observed so far)
4. **Test Claude 3 Haiku** if cost/speed optimization is needed

## References

- [AWS Bedrock Model Support](https://docs.aws.amazon.com/bedrock/latest/userguide/models-supported.html)
- [RetrieveAndGenerate API Reference](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_RetrieveAndGenerate.html)
- [Anthropic Claude Models](https://docs.anthropic.com/claude/docs/models-overview)
