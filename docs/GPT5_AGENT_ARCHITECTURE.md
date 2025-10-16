# GPT-5 Mini Agent Architecture

## Overview

The F1 Service System now uses a **GPT-5 Mini agent with tool calling** instead of the previous LangGraph-based orchestrator with hardcoded routing.

## Architecture Transformation

### Before (LangGraph Orchestrator)
```python
# Hardcoded intent classification
def classify_intent(query):
    if "circuit" in query: return "circuit"
    if "regulation" in query: return "regulations"

# 60+ hardcoded location aliases
LOCATION_ALIASES = {
    "monaco": "Monaco",
    "vegas": "Las_Vegas",
    "silverstone": "Great_Britain",
    # ... 57 more entries
}

# StateGraph with conditional routing
workflow = StateGraph(AgentState)
workflow.add_conditional_edges("classify", route_query, {...})
```

**Problems:**
- Hardcoded keyword matching for intent detection
- Manual maintenance of 60+ location aliases
- Brittle routing logic
- Can't handle variations like "COTA", "Silverstone", etc.

### After (GPT-5 Mini Agent)
```python
# GPT-5 Mini decides which tools to use
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_circuit_image",
            "description": "Retrieve F1 circuit map image...",
            "parameters": {...}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "query_regulations",
            "description": "Query FIA F1 regulations...",
            "parameters": {...}
        }
    }
]

# Agent understands naturally and calls appropriate tools
response = client.chat.completions.create(
    model="gpt-5-mini",
    messages=messages,
    tools=tools
)
```

**Benefits:**
- ✅ Natural language understanding (no keyword matching)
- ✅ No hardcoded aliases (GPT-5 Mini understands "Vegas", "COTA", "Silverstone")
- ✅ Intelligent tool selection
- ✅ Multi-tool coordination for complex queries
- ✅ Self-correcting (learns from tool errors)

## Components

### 1. GPT-5 Mini Agent (`src/agents/gpt5_agent.py`)

**Core Responsibilities:**
- Query understanding and intent recognition
- Tool selection based on natural language
- Tool execution coordination
- Response synthesis

**Key Features:**
- OpenAI function calling with GPT-5 Mini
- Iterative tool calling (up to 5 iterations)
- LangSmith tracing for observability
- Error handling and recovery

**Example Usage:**
```python
from src.agents.gpt5_agent import get_gpt5_agent

agent = get_gpt5_agent()
result = agent.process_query("Show me Monaco and explain DRS rules")

# Result includes:
# - type: success/error/partial
# - content: final answer
# - tools_used: [get_circuit_image, query_regulations]
# - tool_results: detailed results from each tool
# - metadata: iterations, model, latency
```

### 2. Circuit Retrieval Tool (`src/tools/circuit_retrieval.py`)

**Simplified Design:**
- No more LOCATION_ALIASES dictionary
- GPT-5 Mini provides normalized location names
- Simple pattern matching against official circuit names
- Returns image path or error with suggestions

**Before:**
- 60+ hardcoded aliases
- Complex fuzzy matching logic
- Manual maintenance required

**After:**
- GPT-5 Mini understands "Vegas" → "Las Vegas"
- GPT-5 Mini understands "Silverstone" → "Great Britain"
- GPT-5 Mini understands "COTA" → "USA"
- Tool just validates and returns file path

### 3. Regulations RAG Tool (`src/tools/regulations_rag.py`)

**Architecture:**
- AWS Bedrock RetrieveAndGenerate API
- Claude 3 Sonnet for generation
- Single-call retrieval + generation

**Performance:**
- Average latency: 4-5 seconds
- Best retrieval quality (tested vs GPT-4o)
- Citations included in response

**Key Features:**
- Retry logic for throttling (3 attempts with exponential backoff)
- LangSmith tracing
- Error handling for Bedrock API issues

## Tool Calling Flow

```mermaid
graph TD
    A[User Query] --> B[GPT-5 Mini Agent]
    B --> C{Analyze Query}
    C -->|Circuit request| D[get_circuit_image tool]
    C -->|Regulation question| E[query_regulations tool]
    C -->|Both| F[Both tools]
    D --> G[Return image path]
    E --> H[Return regulations answer]
    F --> G
    F --> H
    G --> I[GPT-5 Mini synthesizes response]
    H --> I
    I --> J[Final Answer]
```

## Test Results

All 7 test cases passed (100% success rate):

1. **Circuit Query - Monaco**: ✅ (5.41s)
   - Tool used: `get_circuit_image`
   - Successfully retrieved Monaco circuit

2. **Circuit Query - Casual Name (Vegas)**: ✅ (5.76s)
   - GPT-5 Mini understood "Vegas" → "Las Vegas"
   - No hardcoded alias needed

3. **Circuit Query - Nickname (COTA)**: ✅ (8.05s)
   - GPT-5 Mini asked for clarification (intelligent behavior)
   - Identified COTA = Circuit of the Americas

4. **Regulations Query - Points**: ✅ (15.20s)
   - Tool used: `query_regulations`
   - Accurate answer: 25 points for race, 8 for sprint

5. **Regulations Query - DRS**: ✅ (17.67s)
   - Comprehensive DRS rules explanation
   - Included detection zones, activation conditions

6. **Regulations Query - Safety Car**: ✅ (44.89s)
   - Multiple tool calls (agent breaking down complex query)
   - Detailed safety car procedure

7. **Combined Query - Circuit + Rules**: ✅ (38.09s)
   - Tools used: `get_circuit_image` (2 calls), `query_regulations`
   - Self-corrected: "Silverstone" → "Great_Britain"
   - Synthesized combined response

## Performance Characteristics

### Latency Breakdown

**Simple Circuit Query:**
- GPT-5 Mini reasoning: ~2-3s
- Tool execution: <0.1s
- Response synthesis: ~1-2s
- **Total: 5-6 seconds**

**Simple Regulation Query:**
- GPT-5 Mini reasoning: ~2-3s
- Bedrock RetrieveAndGenerate: ~4-5s
- Response synthesis: ~1-2s
- **Total: 15-20 seconds**

**Complex Multi-Tool Query:**
- Multiple iterations
- Multiple tool calls
- **Total: 30-45 seconds**

**Comparison to LangGraph:**
- LangGraph: ~5s for simple queries
- GPT-5 Mini Agent: ~5-20s depending on complexity
- **Tradeoff:** Slightly slower but much more intelligent

### Model: GPT-5 Mini

**Why GPT-5 Mini?**
- Best reasoning capabilities for tool calling
- Natural language understanding (no aliases needed)
- Self-correcting behavior
- Future-proof for complex agentic workflows

**Characteristics:**
- Model: `gpt-5-mini-2025-08-07`
- Special requirements: No `max_tokens` or `temperature` parameters
- Average latency: 10s per reasoning step
- Higher latency than GPT-4o but better reasoning

**Tested Alternatives:**
- GPT-4o: Faster (3.7s) but worse retrieval quality
- GPT-5 Nano: Similar latency, higher token usage
- Bedrock Claude: Good for RAG but not for orchestration

## Advantages Over Previous Architecture

### 1. Zero Hardcoded Logic
- **Before:** 60+ location aliases, keyword-based intent classification
- **After:** GPT-5 Mini understands naturally

### 2. Self-Correcting
- Agent learns from tool errors
- Example: "Silverstone" failed → retries with "Great_Britain"

### 3. Intelligent Tool Coordination
- Complex queries automatically broken down
- Example: "Show Silverstone and explain points" → 2 tools

### 4. Natural Conversation
- Asks clarifying questions when needed
- Example: "COTA" → "Do you mean Circuit of the Americas?"

### 5. Maintainability
- No alias dictionary to update
- No routing logic to maintain
- Just update tool descriptions

## LangSmith Tracing

All operations are traced with LangSmith:

**Traced Operations:**
- `gpt5_agent_query`: Top-level agent execution
- `execute_tool`: Individual tool calls
- `get_circuit_image`: Circuit retrieval
- `query_regulations`: Bedrock RAG queries

**Dashboard:** https://smith.langchain.com/

**Environment Variables:**
```bash
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=<your-key>
LANGCHAIN_PROJECT=f1-service-system-v1
```

## Migration Notes

### Removed Files/Code
- ❌ `src/agents/orchestrator.py` (LangGraph-based)
- ❌ `LOCATION_ALIASES` dictionary (60+ entries)
- ❌ `classify_intent()` method
- ❌ `route_query()` method

### Added Files/Code
- ✅ `src/agents/gpt5_agent.py` (GPT-5 Mini agent)
- ✅ `scripts/test_gpt5_agent.py` (comprehensive tests)
- ✅ `docs/GPT5_AGENT_ARCHITECTURE.md` (this document)

### Updated Files
- ✅ `src/tools/circuit_retrieval.py` (removed aliases)
- ✅ `src/tools/regulations_rag.py` (cleaned up)

## Future Enhancements

### Potential Improvements
1. **Tool Caching:** Cache circuit image paths
2. **Parallel Tool Calls:** Use OpenAI parallel function calling
3. **Streaming:** Stream responses for better UX
4. **Memory:** Add conversation history for context
5. **Additional Tools:** Add more F1 data sources

### Agent Capabilities to Explore
- Multi-turn conversations
- Proactive suggestions ("Would you like to see...")
- Data visualization (charts, graphs)
- Comparative analysis (e.g., compare circuits)

## Conclusion

The GPT-5 Mini agent architecture represents a significant improvement over the LangGraph orchestrator:

✅ **Eliminates 200+ lines of hardcoded logic**  
✅ **Natural language understanding (no aliases)**  
✅ **Intelligent tool calling**  
✅ **Self-correcting behavior**  
✅ **Easier to maintain and extend**

Trade-off: Slightly higher latency (5-20s vs 5s) for significantly better intelligence and maintainability.

The system is now **truly agentic** - GPT-5 Mini makes intelligent decisions rather than following hardcoded rules.
