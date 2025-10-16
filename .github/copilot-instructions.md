# F1 Service System - AI Agent Instructions

## Project Overview
This is an F1 information service system combining LLM agents, RAG (Retrieval-Augmented Generation), and circuit visualization. The system routes user queries to appropriate tools: circuit image retrieval or F1 regulations knowledge base.

**Architecture Pattern**: LLM Agent with Tool Calling. Use Langgraph and LangSmith
- User query → OpenAI LLM Agent → Tool routing → Response aggregation → Streamlit UI

## Core Components (Planned)

### 1. LLM Agent Layer (OpenAI)
- Primary orchestrator for query understanding and tool selection
- Must implement function calling/tools API pattern
- Route queries to appropriate handlers based on intent detection

### 2. Circuit Image Retrieval Tool
- Data source: `f1_2025_circuit_maps/` (24 circuits, `.webp` format)
- File naming convention: `{Location}_Circuit.webp` (e.g., `Miami_Circuit.webp`)
- Tool should handle location name normalization (case-insensitive, handle variants like "Vegas" → "Las_Vegas")
- Return webp image paths for Streamlit display

### 3. Regulations RAG Tool
- Integration: AWS Bedrock Knowledge Base + Pinecone vector DB
- Handle F1 regulation queries (rules, technical specs, sporting regulations)
- Implement retrieval → generation pipeline

### 4. Frontend (Streamlit)
- Single interface displaying both image and text responses
- Must support rendering `.webp` images
- Show LLM-generated responses from knowledge base queries

## Critical Development Requirements

### Dependency Management
**ALWAYS use Poetry** - never pip directly:
```bash
poetry add <package>           # Add dependencies
poetry install                 # Install from pyproject.toml
poetry run python <script>     # Run scripts in poetry env
poetry shell                   # Activate virtual environment
```

### Logging Convention
**NEVER use `print()` statements** - use Loguru exclusively with color-coded log levels:
```python
from loguru import logger

# Good ✓
logger.info("Processing query: {}", user_query)
logger.error("Failed to retrieve circuit image: {}", error)
logger.debug("Tool selection result: {}", tool_name)

# Bad ✗
print("Processing query:", user_query)
```
### Tracing
Use Langsmith tracing for observability:

## Implementation Guidelines

### Project Structure (To Be Created)
```
src/
├── agents/
│   └── orchestrator.py      # OpenAI agent with tool calling
├── tools/
│   ├── circuit_retrieval.py # Circuit image tool
│   └── regulations_rag.py   # Bedrock + Pinecone integration
├── ui/
│   └── app.py              # Streamlit application
├── config/
│   └── settings.py         # Environment vars, API keys
└── utils/
    └── logger.py           # Loguru configuration
```

### Tool Design Pattern
Each tool should follow this interface:
```python
from typing import Dict, Any

def tool_name(query: str) -> Dict[str, Any]:
    """
    Returns: {
        "type": "image" | "text",
        "content": <path_or_text>,
        "metadata": {...}
    }
    """
```

### Circuit Retrieval Implementation Notes
- 24 total circuits available (2025 season)
- Location names: Abu_Dhabi, Australia, Austria, Bahrain, Baku, Belgium, Brazil, Canada, China, Emilia_Romagna, Great_Britain, Hungary, Italy, Japan, Las_Vegas, Mexico, Miami, Monaco, Netherlands, Qatar, Saudi_Arabia, Singapore, Spain, USA
- Handle common aliases (e.g., "British GP" → Great_Britain, "COTA" → USA)
- Return error message if circuit not found, don't fail silently

### AWS/Pinecone Integration
- Store credentials in environment variables (never hardcode)
- Use `boto3` for Bedrock Knowledge Base
- Configure Pinecone client with appropriate index name
- Implement proper error handling for API failures

### Bedrock Model Configuration
- **Embedding Model**: Amazon Titan Text Embeddings V2 (`amazon.titan-embed-text-v2:0`)
  - Used by Bedrock Knowledge Base for semantic chunking and vector storage
- **Generation Model**: Anthropic Claude 3 Sonnet (`anthropic.claude-3-sonnet-20240229-v1:0`)
  - Used for RetrieveAndGenerate API calls
  - NOTE: Claude 3.5 Sonnet v2 requires inference profiles and is NOT supported for on-demand RetrieveAndGenerate
  - Always use settings.bedrock_generation_model from environment variables
- **Rate Limiting**: Implement 10-15 second delays between requests to avoid throttling
- **Retry Logic**: Use `tenacity` library for handling 429 ThrottlingException errors

## Development Workflow

### Initial Setup (Not Yet Done)
1. Initialize Poetry: `poetry init` or create `pyproject.toml`
2. Add core dependencies: `openai`, `boto3`, `pinecone-client`, `streamlit`, `loguru`
3. Set up `.env` file for API keys (OpenAI, AWS, Pinecone)
4. Configure Loguru in `utils/logger.py` with appropriate log levels

### Testing Considerations
- Test circuit retrieval with valid/invalid location names
- Mock AWS/Pinecone calls for unit tests
- Test OpenAI tool calling with sample queries
- Verify Streamlit renders both image and text responses

## Query Routing Logic
The LLM agent should route based on these patterns:
- **Circuit queries**: Keywords like "circuit", "track", "layout", "map", specific location names
  - Example: "Show me the Miami circuit" → Circuit Retrieval Tool
- **Regulation queries**: Keywords like "rules", "regulation", "technical", "sporting", "FIA"
  - Example: "What are the DRS rules?" → Regulations RAG Tool
- **Hybrid queries**: May require both tools
  - Example: "Show me Monaco and explain the safety car rules"

## Current State
- ✅ Circuit images available (24 circuits in `.webp` format)
- ✅ Architecture defined in README.md
- ⏳ No Python implementation yet
- ⏳ Poetry project not initialized
- ⏳ AWS/Pinecone integration pending

When implementing, start with the circuit retrieval tool (simplest, no external APIs), then agent orchestrator, then RAG integration, and finally Streamlit UI.
