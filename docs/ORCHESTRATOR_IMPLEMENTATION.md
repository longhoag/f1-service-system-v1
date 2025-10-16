# F1 Agent Orchestrator Implementation

## Overview

The F1 Agent Orchestrator is implemented using **LangGraph** for state machine-based agent orchestration and **LangSmith** for comprehensive tracing and observability.

## Architecture

```
User Query
    ↓
F1AgentOrchestrator (LangGraph)
    ↓
classify_intent
    ↓
route_query
    ├─→ execute_circuit → CircuitRetrieval
    ├─→ execute_regulations → RegulationsRAG → AWS Bedrock KB
    └─→ execute_both → Both tools
    ↓
synthesize_response
    ↓
Final Response
```

## Components

### 1. F1AgentOrchestrator (`src/agents/orchestrator.py`)

**LangGraph State Machine** with the following nodes:
- `classify_intent`: Determines query type (circuit/regulations/both)
- `execute_circuit`: Retrieves circuit images
- `execute_regulations`: Queries Bedrock Knowledge Base
- `synthesize_response`: Combines results into final response

**Intent Classification**:
- Circuit keywords: "circuit", "track", "map", "show", location names
- Regulations keywords: "rule", "penalty", "points", "DRS", "safety car", etc.
- Combined: Both keyword types present

### 2. RegulationsRAG Tool (`src/tools/regulations_rag.py`)

**Features**:
- AWS Bedrock Knowledge Base integration
- LangSmith tracing for Bedrock API calls
- Retry logic with exponential backoff (tenacity)
- Dynamic parameter tuning based on query type
- Custom prompt templates for better responses

**Key Methods**:
- `query_regulations()`: Main entry point (traced)
- `_retrieve_and_generate()`: Bedrock API call (traced, retryable)
- `_get_retrieval_config()`: Adaptive retrieval params
- `_get_generation_config()`: Query-specific generation settings

**Retrieval Configuration**:
- Factual queries: 3 chunks, HYBRID search
- Explanation queries: 5 chunks, HYBRID search
- Temperature: 0.3 (factual) to 0.7 (explanatory)

### 3. CircuitRetrieval Tool (`src/tools/circuit_retrieval.py`)

**Features**:
- 24 F1 2025 circuits supported
- Extensive location alias mapping (60+ aliases)
- LangSmith tracing for retrieval operations
- Fuzzy matching (direct, alias, partial word matching)

**Supported Circuits**:
Abu Dhabi, Australia, Austria, Bahrain, Baku, Belgium, Brazil, Canada, China, Emilia Romagna, Great Britain, Hungary, Italy, Japan, Las Vegas, Mexico, Miami, Monaco, Netherlands, Qatar, Saudi Arabia, Singapore, Spain, USA

## LangSmith Tracing

### What Gets Traced

1. **Orchestrator Level**:
   - `process_query`: Full query execution
   - `classify_intent`: Intent classification
   - `execute_circuit`: Circuit tool execution
   - `execute_regulations`: Regulations tool execution
   - `synthesize_response`: Response combination

2. **Regulations RAG Level**:
   - `query_regulations`: RAG entry point
   - `retrieve_and_generate`: Bedrock API call
   - `extract_sources`: Citation processing

3. **Circuit Retrieval Level**:
   - `get_circuit_image`: Image retrieval
   - `normalize_location`: Location matching

### Trace Metadata

Each trace includes:
- Execution time
- Input/output data
- Error information (if any)
- Custom tags (e.g., "circuit", "regulations", "bedrock")

### Viewing Traces

1. Go to https://smith.langchain.com/
2. Navigate to your project: `f1-service-system-v1`
3. View traces with full execution details
4. Analyze performance, errors, and bottlenecks

## Configuration

### Environment Variables

```bash
# LangSmith Tracing
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=your_langsmith_api_key_here
LANGCHAIN_PROJECT=f1-service-system-v1

# AWS Bedrock
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
BEDROCK_KNOWLEDGE_BASE_ID=your_kb_id
BEDROCK_GENERATION_MODEL=anthropic.claude-3-sonnet-20240229-v1:0
```

### Getting LangSmith API Key

1. Sign up at https://smith.langchain.com/
2. Go to Settings → API Keys
3. Create a new API key
4. Add to `.env` file

## Usage

### Basic Usage

```python
from src.agents.orchestrator import get_orchestrator

# Initialize orchestrator
orchestrator = get_orchestrator()

# Process query
result = orchestrator.process_query("Show me the Monaco circuit")

print(result)
# {
#   "query": "Show me the Monaco circuit",
#   "intent": "circuit",
#   "response": {
#     "type": "image",
#     "content": "/path/to/Monaco_Circuit.webp",
#     "message": "Circuit map: Monaco",
#     "metadata": {...}
#   },
#   "metadata": {
#     "circuit_executed": True,
#     "regulations_executed": False
#   }
# }
```

### Query Examples

**Circuit Query**:
```python
result = orchestrator.process_query("Show me Silverstone")
# Intent: circuit
# Returns: Circuit image path
```

**Regulations Query**:
```python
result = orchestrator.process_query("What are the DRS rules?")
# Intent: regulations
# Returns: Generated answer from Bedrock KB
```

**Combined Query**:
```python
result = orchestrator.process_query(
    "Show me Monaco and explain the safety car procedure"
)
# Intent: both
# Returns: Circuit image + regulations answer
```

## Testing

### Run Orchestrator Tests

```bash
poetry run python scripts/test_orchestrator.py
```

This tests:
- Intent classification accuracy
- Circuit retrieval
- Regulations RAG queries
- Combined queries
- Error handling

### Test Output

```
Test 1/5: Circuit-only query
Query: 'Show me the Monaco circuit'
Expected intent: circuit
✓ Actual intent: circuit
✓ Intent classification CORRECT
📸 Image: Circuit map: Monaco

Test 2/5: Regulations-only query
Query: 'What are the DRS activation rules?'
Expected intent: regulations
✓ Actual intent: regulations
✓ Intent classification CORRECT
📝 Text response (245 chars):
   DRS can only be activated in designated zones...
   Sources: 2025_fia_formula_1_sporting_regulations.pdf

TEST SUMMARY
Tests completed: 5/5
Correct intent classification: 5/5
🎉 All tests passed!
```

## Performance

### Typical Response Times

- **Circuit retrieval**: <100ms (local file lookup)
- **Regulations RAG**: 2-5s (Bedrock API call)
- **Combined queries**: 3-6s (sequential execution)

### Optimization

1. **Caching**: Circuit images are static (instant subsequent retrievals)
2. **Retry Logic**: Exponential backoff for Bedrock throttling
3. **Adaptive Retrieval**: Fewer chunks for factual queries (faster)
4. **Parallel Execution**: Could parallelize circuit + regulations (future)

## Error Handling

### Graceful Degradation

1. **Circuit not found**: Returns friendly error message with available circuits
2. **Bedrock throttling**: Automatic retry with exponential backoff (3 attempts)
3. **Network errors**: Returns error response without crashing
4. **Invalid KB ID**: Caught during initialization

### Error Response Format

```python
{
    "type": "error",
    "content": "I couldn't identify a circuit from: 'xyz'",
    "metadata": {
        "status": "not_found",
        "available_circuits": [...]
    }
}
```

## LangGraph State Management

### AgentState Structure

```python
class AgentState(TypedDict):
    query: str                      # User query
    intent: str                     # "circuit" | "regulations" | "both"
    circuit_result: Dict[str, Any]  # Circuit tool result
    regulations_result: Dict[str, Any]  # RAG tool result
    final_response: str             # Synthesized response
    messages: Annotated[list, operator.add]  # Message history
```

### State Transitions

```
Initial State
    ↓
classify_intent (updates intent, messages)
    ↓
route_query (reads intent)
    ↓
execute_circuit/regulations (updates circuit_result/regulations_result)
    ↓
synthesize_response (updates final_response)
    ↓
Final State
```

## Future Enhancements

### Planned

1. **OpenAI Function Calling**: Replace keyword-based intent with LLM classification
2. **Parallel Execution**: Run circuit + regulations tools simultaneously
3. **Conversation Memory**: Support multi-turn conversations
4. **Caching Layer**: Redis for Bedrock responses
5. **Streaming Responses**: Stream Bedrock generation for better UX

### Advanced Tracing

1. **Custom Metrics**: Track retrieval precision, generation quality
2. **A/B Testing**: Compare different retrieval configurations
3. **Cost Tracking**: Monitor Bedrock API costs per query
4. **User Feedback**: Collect thumbs up/down for quality improvement

## Troubleshooting

### LangSmith traces not appearing

1. Check `LANGCHAIN_TRACING_V2=true` in `.env`
2. Verify `LANGCHAIN_API_KEY` is valid
3. Ensure project name matches: `LANGCHAIN_PROJECT=f1-service-system-v1`
4. Check network connectivity to api.smith.langchain.com

### Bedrock API errors

1. **ValidationException**: Check generation model is Claude 3 Sonnet (not 3.5 v2)
2. **ThrottlingException**: Retry logic should handle this automatically
3. **AccessDeniedException**: Verify AWS credentials and model access permissions

### Circuit images not found

1. Verify `f1_2025_circuit_maps/` directory exists in project root
2. Check file naming: `{Location}_Circuit.webp`
3. Use absolute paths (handled automatically)

## Dependencies

```toml
langgraph = "^0.6.10"
langsmith = "^0.4.36"
langchain-core = "^0.3.79"
langchain-aws = "^0.2.35"
boto3 = "^1.28.0"
tenacity = "^9.1.2"
loguru = "^0.7.0"
```

## Next Steps

1. **Test the orchestrator**: `poetry run python scripts/test_orchestrator.py`
2. **Check LangSmith traces**: Visit https://smith.langchain.com/
3. **Implement Streamlit UI**: Use orchestrator in `src/ui/app.py`
4. **Add conversation memory**: Extend AgentState for multi-turn dialogs
5. **Deploy**: Containerize with Docker for production
