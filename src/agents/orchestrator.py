"""
F1 Agent Orchestrator with OpenAI Tool Calling.
Intelligent agent that binds tools for:
- Circuit image retrieval
- F1 regulations queries via Bedrock

No hardcoded routing or aliases - LLM understands queries naturally.
Supports both GPT-4o and GPT-5 Mini models.
"""

import json
from typing import Dict, Any, List, Optional
from loguru import logger
from langsmith import traceable
from openai import OpenAI

from src.config.settings import settings
from src.tools.circuit_retrieval import get_circuit_retrieval
from src.tools.regulations_rag import get_regulations_rag


class Orchestrator:
    """
    F1 agent orchestrator with tool calling for intelligent query routing.
    
    Uses OpenAI function calling to intelligently route queries to:
    - get_circuit_image: Retrieve F1 circuit map images
    - query_regulations: Query F1 regulations via AWS Bedrock
    
    No hardcoded logic - agent decides which tools to use based on query.
    """

    def __init__(self):
        """Initialize orchestrator agent with tools."""
        logger.info("Initializing F1 Orchestrator Agent with tool calling")
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        logger.info(f"  • Model: {self.model}")
        
        # Initialize tools
        try:
            self.circuit_tool = get_circuit_retrieval()
            logger.info("  ✓ Circuit retrieval tool loaded")
        except Exception as e:
            logger.error(f"Failed to initialize circuit tool: {e}")
            raise
        
        try:
            self.regulations_tool = get_regulations_rag()
            logger.info("  ✓ Regulations RAG tool loaded")
        except Exception as e:
            logger.error(f"Failed to initialize regulations tool: {e}")
            raise
        
        # Define tool schemas for OpenAI function calling
        self.tools = self._define_tools()
        logger.info(f"  ✓ {len(self.tools)} tools bound to agent")
        
        logger.success("F1 Orchestrator Agent initialized")

    def _define_tools(self) -> List[Dict[str, Any]]:
        """
        Define OpenAI function calling schemas for available tools.
        
        Returns:
            List of tool definitions in OpenAI format
        """
        # Get available circuits for description
        available_circuits = self.circuit_tool.list_available_circuits()
        circuits_str = ", ".join(available_circuits[:10]) + "..."
        
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_circuit_image",
                    "description": (
                        f"Get F1 circuit map image. Available: {circuits_str}. "
                        f"Returns .webp image path. Use for queries like 'show Monaco', 'display Vegas circuit'. "
                        f"Pass location as: Monaco, Las_Vegas, Great_Britain, USA (for COTA), etc."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "Circuit name: Monaco, Las_Vegas, Great_Britain, USA, etc."
                            }
                        },
                        "required": ["location"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "query_regulations",
                    "description": (
                        "Query FIA F1 regulations. Use for rules, points, DRS, safety car, penalties, etc. "
                        "Returns official FIA regulation text with citations. Fast: 4-5s response."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "question": {
                                "type": "string",
                                "description": "Regulation question (e.g., 'points for 1st', 'DRS rules')"
                            }
                        },
                        "required": ["question"]
                    }
                }
            }
        ]

    @traceable(name="gpt5_agent_query", tags=["agent", "gpt5", "tool-calling"])
    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process user query using GPT-5 Mini with tool calling.
        
        Agent decides which tools to call based on query understanding.
        No hardcoded routing logic - pure AI reasoning.
        
        Args:
            query: User's F1 information query
            
        Returns:
            Dict with response, tools_used, and metadata
        """
        logger.info(f"Processing query: '{query}'")
        
        # Initialize conversation with highly optimized system prompt
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an ultra-fast F1 assistant. RULES:\n"
                    "1. Call tools IMMEDIATELY in first response - NO explanation before calling\n"
                    "2. For circuit queries: call get_circuit_image(location) ONCE only\n"
                    "3. For regulation queries: call query_regulations(question) ONCE only\n"
                    "4. For combined queries: call BOTH tools in PARALLEL (same response)\n"
                    "5. After tool results: give SHORT 1-2 sentence summary\n"
                    "6. NEVER ask follow-up questions - just use the tools\n"
                    "7. Trust tool results - don't verify or double-check\n"
                    "SPEED IS CRITICAL. Be decisive and concise."
                )
            },
            {
                "role": "user",
                "content": query
            }
        ]
        
        tools_used = []
        tool_results = {}
        max_iterations = 2  # Hard limit: 1 for tools, 1 for response
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            logger.debug(f"Agent iteration {iteration}")
            
            try:
                # Call model with tools
                # Optimized for maximum speed with guardrails
                is_gpt5 = self.model.startswith('gpt-5')
                
                if is_gpt5:
                    # GPT-5: No parameter support, but still fast with good prompts
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        tools=self.tools,
                        parallel_tool_calls=True  # GPT-5 supports parallel calls
                    )
                else:
                    # GPT-4o: Full optimization
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        tools=self.tools,
                        temperature=0.05,  # Ultra-low = fastest, most deterministic
                        max_tokens=150,  # Very strict limit (was 300)
                        parallel_tool_calls=True,  # Call multiple tools at once
                        top_p=0.85,  # Focus on most likely tokens
                        frequency_penalty=0.0,  # No penalty for speed
                        presence_penalty=0.0  # No penalty for speed
                    )
                
                message = response.choices[0].message
                
                # Check if agent wants to call tools
                if not message.tool_calls:
                    # Agent provided final answer
                    logger.success(f"Agent completed in {iteration} iterations")
                    return {
                        "type": "success",
                        "content": message.content,
                        "tools_used": tools_used,
                        "tool_results": tool_results,
                        "metadata": {
                            "iterations": iteration,
                            "model": self.model,
                            "query": query
                        }
                    }
                
                # Add assistant message to conversation
                messages.append({
                    "role": "assistant",
                    "content": message.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in message.tool_calls
                    ]
                })
                
                # Execute tool calls (parallel execution)
                tool_call_results = []
                for tool_call in message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)
                    
                    logger.debug(f"Agent calling tool: {tool_name}({tool_args})")
                    tools_used.append(tool_name)
                    
                    # Execute tool
                    result = self._execute_tool(tool_name, tool_args)
                    tool_results[tool_name] = result
                    
                    # Add tool result to conversation
                    tool_call_results.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result)
                    })
                    
                    logger.debug(f"Tool {tool_name} result: {result.get('type')}")
                
                # Add all tool results at once (more efficient)
                messages.extend(tool_call_results)
                
                # Guardrail: If we have tool results and this is iteration 1,
                # force final response in next iteration
                if iteration == 1 and tool_results:
                    messages.append({
                        "role": "system",
                        "content": (
                            "FINAL RESPONSE NOW. Use tool results. "
                            "1 sentence max. No explanations."
                        )
                    })
                
            except Exception as e:
                logger.error(f"Agent error on iteration {iteration}: {e}")
                return {
                    "type": "error",
                    "content": f"Agent error: {str(e)}",
                    "tools_used": tools_used,
                    "metadata": {
                        "error": str(e),
                        "iteration": iteration,
                        "query": query
                    }
                }
        
        # Max iterations reached
        logger.warning(f"Agent reached max iterations ({max_iterations})")
        return {
            "type": "partial",
            "content": "I needed to make too many tool calls. Please try rephrasing your query.",
            "tools_used": tools_used,
            "tool_results": tool_results,
            "metadata": {
                "iterations": max_iterations,
                "reason": "max_iterations_reached",
                "query": query
            }
        }

    @traceable(name="execute_tool", tags=["tool-execution"])
    def _execute_tool(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool function with given arguments.
        Optimized for speed with minimal overhead.
        
        Args:
            tool_name: Name of tool to execute
            args: Arguments for tool
            
        Returns:
            Tool execution result
        """
        logger.debug(f"Executing tool: {tool_name}")  # Changed to debug for less overhead
        
        try:
            if tool_name == "get_circuit_image":
                location = args.get("location", "")
                result = self.circuit_tool.get_circuit_image(location)
                # Only log if error for speed
                if result.get('type') == 'error':
                    logger.warning(f"Circuit tool error: {result.get('metadata', {}).get('status')}")
                return result
                
            elif tool_name == "query_regulations":
                question = args.get("question", "")
                result = self.regulations_tool.query_regulations(question)
                # Only log if error for speed
                if result.get('type') == 'error':
                    logger.warning(f"Regulations tool error: {result.get('metadata', {}).get('status')}")
                return result
                
            else:
                logger.error(f"Unknown tool: {tool_name}")
                return {
                    "type": "error",
                    "content": f"Unknown tool: {tool_name}",
                    "metadata": {"error": "unknown_tool"}
                }
                
        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            return {
                "type": "error",
                "content": str(e),
                "metadata": {"error": str(e), "tool": tool_name}
            }


# Singleton instance
_orchestrator_instance: Optional[Orchestrator] = None


def get_orchestrator() -> Orchestrator:
    """Get or create singleton instance of Orchestrator."""
    global _orchestrator_instance
    
    if _orchestrator_instance is None:
        _orchestrator_instance = Orchestrator()
    
    return _orchestrator_instance
