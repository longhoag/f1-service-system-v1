# F1 Service System v1

An intelligent F1 information service powered by **GPT-5 Mini agent** with tool calling. The system provides circuit maps and regulations information through natural language queries.

## 🏎️ Features

- **GPT-5 Mini Agent**: Intelligent query understanding and tool orchestration
- **Circuit Image Retrieval**: Access to 24 F1 2025 circuit maps (.webp format)
- **Regulations RAG**: Query FIA F1 regulations via AWS Bedrock Knowledge Base
- **Natural Language**: No hardcoded aliases - understands "Vegas", "COTA", "Silverstone" naturally
- **LangSmith Tracing**: Full observability of agent and tool operations

## 🏗️ Architecture

```
User Query
    ↓
GPT-5 Mini Agent (OpenAI)
    ↓
  ┌─────────────────────┐
  │  Tool Selection     │
  └─────────────────────┘
         ↓         ↓
    Circuit    Regulations
    Retrieval      RAG
         ↓         ↓
    .webp     AWS Bedrock
    Images    Knowledge Base
         ↓         ↓
    ┌─────────────────────┐
    │  Response Synthesis │
    └─────────────────────┘
         ↓
    Streamlit UI
```

**Key Components:**
1. **GPT-5 Mini Agent** (`src/agents/gpt5_agent.py`)
   - Natural language query understanding
   - Intelligent tool calling
   - Multi-tool coordination
   - Self-correcting behavior

2. **Circuit Retrieval Tool** (`src/tools/circuit_retrieval.py`)
   - 24 F1 2025 circuit maps
   - Dynamic location understanding (no hardcoded aliases)
   - Image path resolution

3. **Regulations RAG Tool** (`src/tools/regulations_rag.py`)
   - AWS Bedrock RetrieveAndGenerate API
   - Claude 3 Sonnet generation
   - FIA F1 regulations knowledge base
   - Citation support

## 📋 Requirements

- **Python**: 3.10+
- **Poetry**: Dependency management
- **OpenAI API**: GPT-5 Mini access
- **AWS Bedrock**: Knowledge Base access
- **LangSmith**: Tracing and observability

## 🚀 Setup

### 1. Install Dependencies
```bash
poetry install
```

### 2. Configure Environment Variables
Create `.env` file:
```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-5-mini

# AWS Bedrock Configuration
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-1
BEDROCK_KNOWLEDGE_BASE_ID=BJGTYMNOBH
BEDROCK_GENERATION_MODEL=anthropic.claude-3-sonnet-20240229-v1:0

# LangSmith Tracing
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=...
LANGCHAIN_PROJECT=f1-service-system-v1
```

### 3. Test the Agent
```bash
poetry run python scripts/test_gpt5_agent.py
```

Expected output:
```
🏎️ GPT-5 MINI AGENT TEST SUITE
Testing tool calling with F1 information queries

TEST 1/7: Circuit Query - Monaco
⏱️  Response Time: 5.41s
✅ PASS

...

Total: 7/7 tests passed (100%)
🎉 All tests passed!
```

## 💡 Usage Examples

### Circuit Queries
```python
from src.agents.gpt5_agent import get_gpt5_agent

agent = get_gpt5_agent()

# Simple circuit query
result = agent.process_query("Show me the Monaco circuit")
# Tools used: [get_circuit_image]
# Returns: Image path to Monaco_Circuit.webp

# Casual name
result = agent.process_query("Can I see the Vegas track?")
# Agent understands: Vegas → Las Vegas
# Returns: Image path to Las_Vegas_Circuit.webp

# Nickname
result = agent.process_query("Display COTA circuit")
# Agent understands: COTA → Circuit of the Americas → USA
# Returns: Image path to USA_Circuit.webp
```

### Regulations Queries
```python
# Points system
result = agent.process_query("How many points for 1st place?")
# Tools used: [query_regulations]
# Returns: "25 points for race, 8 points for sprint..."

# DRS rules
result = agent.process_query("What are the DRS rules?")
# Returns: Comprehensive DRS explanation with citations

# Safety car
result = agent.process_query("Explain safety car procedure")
# Returns: Detailed safety car rules from FIA regulations
```

### Combined Queries
```python
# Multi-tool coordination
result = agent.process_query("Show me Silverstone and explain the points system")
# Tools used: [get_circuit_image, query_regulations]
# Agent coordinates both tools and synthesizes response
```

## 🧪 Testing

### Run Full Test Suite
```bash
poetry run python scripts/test_gpt5_agent.py
```

### Test Individual Components
```bash
# Test circuit retrieval
poetry run python -c "from src.tools.circuit_retrieval import get_circuit_retrieval; print(get_circuit_retrieval().get_circuit_image('Monaco'))"

# Test regulations RAG
poetry run python -c "from src.tools.regulations_rag import get_regulations_rag; print(get_regulations_rag().query_regulations('How many points for 1st?'))"
```

### Model Performance Tests
```bash
# Compare model latencies
poetry run python scripts/test_model_latency.py

# Compare accuracy
poetry run python scripts/test_bedrock_vs_gpt4o.py
```

## 📊 Performance

### Latency Benchmarks
- **Simple Circuit Query**: 5-6 seconds
- **Simple Regulation Query**: 15-20 seconds (includes Bedrock call)
- **Complex Multi-Tool Query**: 30-45 seconds

### Model: GPT-5 Mini
- **Reasoning**: ~10s per iteration
- **Benefits**: Best natural language understanding, no hardcoded logic
- **Tradeoff**: Slower than GPT-4o (3.7s) but more intelligent

### Tool Performance
- **Circuit Retrieval**: <0.1s (local file access)
- **Bedrock RAG**: 4-5s average (AWS API call)

See `docs/MODEL_COMPARISON.md` and `docs/ACCURACY_COMPARISON.md` for detailed analysis.

## 📖 Documentation

- **[GPT-5 Agent Architecture](docs/GPT5_AGENT_ARCHITECTURE.md)**: Detailed architecture explanation
- **[Model Comparison](docs/MODEL_COMPARISON.md)**: Performance analysis across models
- **[Accuracy Comparison](docs/ACCURACY_COMPARISON.md)**: Quality comparison of RAG approaches

## 🔍 LangSmith Tracing

All agent and tool operations are traced with LangSmith:

**View Traces:** https://smith.langchain.com/

**Traced Operations:**
- `gpt5_agent_query`: Top-level agent execution
- `execute_tool`: Individual tool calls
- `get_circuit_image`: Circuit retrieval
- `query_regulations`: Bedrock RAG queries

## 🛠️ Development Guidelines

### Logging Convention
**Always use Loguru** (never print):
```python
from loguru import logger

logger.info("Processing query: {}", query)
logger.success("Tool executed successfully")
logger.error("Failed to retrieve: {}", error)
logger.debug("Intermediate result: {}", data)
```

### Dependency Management
**Always use Poetry**:
```bash
poetry add <package>      # Add dependency
poetry install            # Install from pyproject.toml
poetry run python script  # Run in poetry environment
```

### Code Style
- Type hints for all functions
- Docstrings for all public methods
- LangSmith @traceable decorators for key operations
- Error handling with try/except blocks

## 🎯 Project Status

### ✅ Completed
- GPT-5 Mini agent with tool calling
- Circuit image retrieval (24 circuits)
- Regulations RAG (AWS Bedrock + Claude 3 Sonnet)
- LangSmith tracing
- Comprehensive testing (7/7 tests passing)
- Model comparison analysis
- Accuracy benchmarking

### 🚧 In Progress
- Streamlit UI implementation

### 📝 Planned
- Conversation history/memory
- Streaming responses
- Additional F1 data sources (race results, standings, etc.)
- Tool result caching
- Parallel tool calling

## 🏗️ Architecture Evolution

### v1.0 (Previous - LangGraph)
- Hardcoded intent classification
- 60+ location aliases
- Keyword-based routing
- StateGraph orchestration

**Problems:**
- Brittle routing logic
- Manual alias maintenance
- Can't handle variations

### v2.0 (Current - GPT-5 Mini Agent)
- Natural language understanding
- Zero hardcoded aliases
- Intelligent tool calling
- Self-correcting behavior

**Benefits:**
- Truly agentic
- Easier to maintain
- Handles natural variations
- Multi-tool coordination

## 📄 License

[LICENSE](LICENSE)

## 🤝 Contributing

Contributions welcome! Please ensure:
- Use Poetry for dependencies
- Use Loguru for logging
- Add tests for new features
- Update documentation

## 🔗 References

- [OpenAI GPT-5 Mini](https://platform.openai.com/docs/models/gpt-5)
- [AWS Bedrock Knowledge Base](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html)
- [LangSmith Documentation](https://docs.smith.langchain.com/)
- [FIA F1 Regulations](https://www.fia.com/regulation/category/110)
```
