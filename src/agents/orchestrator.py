"""
F1 Agent Orchestrator using LangGraph.
Routes queries to appropriate tools (Circuit Retrieval or Regulations RAG).
Implements LangSmith tracing for full observability.
"""

from typing import Dict, Any, TypedDict, Annotated, Literal
import operator
from loguru import logger
from langsmith import traceable
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.tools.circuit_retrieval import get_circuit_retrieval
from src.tools.regulations_rag import get_regulations_rag
from src.utils.logger import setup_logger


# Define agent state
class AgentState(TypedDict):
    """State for the F1 agent orchestrator."""
    query: str
    intent: str
    circuit_result: Dict[str, Any]
    regulations_result: Dict[str, Any]
    final_response: str
    messages: Annotated[list, operator.add]


class F1AgentOrchestrator:
    """
    LangGraph-based orchestrator for F1 information queries.
    Routes queries to circuit retrieval or regulations RAG tools.
    """

    def __init__(self):
        """Initialize the orchestrator with tools and LangGraph workflow."""
        logger.info("Initializing F1 Agent Orchestrator")
        
        # Initialize tools
        try:
            self.circuit_tool = get_circuit_retrieval()
            logger.info("✓ Circuit retrieval tool initialized")
        except Exception as e:
            logger.error(f"Failed to initialize circuit tool: {e}")
            raise
        
        try:
            self.regulations_tool = get_regulations_rag()
            logger.info("✓ Regulations RAG tool initialized")
        except Exception as e:
            logger.error(f"Failed to initialize regulations tool: {e}")
            raise
        
        # Build LangGraph workflow
        try:
            self.app = self._build_graph()
            logger.info("✓ LangGraph workflow compiled")
        except Exception as e:
            logger.error(f"Failed to build graph: {e}")
            raise
        
        logger.success("F1 Agent Orchestrator initialized with LangGraph")

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph state machine for query routing."""
        logger.info("Building LangGraph workflow...")
        
        # Create graph
        workflow = StateGraph(AgentState)
        logger.debug("✓ StateGraph created")
        
        # Add nodes
        workflow.add_node("classify_intent", self.classify_intent)
        workflow.add_node("execute_circuit", self.execute_circuit)
        workflow.add_node("execute_regulations", self.execute_regulations)
        workflow.add_node("synthesize_response", self.synthesize_response)
        logger.debug("✓ Nodes added")
        
        # Set entry point
        workflow.set_entry_point("classify_intent")
        logger.debug("✓ Entry point set")
        
        # Add conditional routing
        workflow.add_conditional_edges(
            "classify_intent",
            self.route_query,
            {
                "circuit": "execute_circuit",
                "regulations": "execute_regulations",
                "both": "execute_circuit",
                "unknown": "synthesize_response"
            }
        )
        
        workflow.add_conditional_edges(
            "execute_circuit",
            lambda state: "regulations" if state["intent"] == "both" else "synthesize",
            {
                "regulations": "execute_regulations",
                "synthesize": "synthesize_response"
            }
        )
        
        workflow.add_edge("execute_regulations", "synthesize_response")
        workflow.add_edge("synthesize_response", END)
        logger.debug("✓ Edges configured")
        
        compiled_graph = workflow.compile()
        logger.debug(f"✓ Graph compiled: {type(compiled_graph)}")
        
        return compiled_graph

    @traceable(name="classify_intent", tags=["orchestrator", "classification"])
    def classify_intent(self, state: AgentState) -> AgentState:
        """Classify user query intent."""
        query = state["query"].lower()
        logger.info(f"Classifying intent for: '{state['query']}'")
        
        circuit_keywords = ["circuit", "track", "map", "layout", "show"]
        regulations_keywords = [
            "rule", "regulation", "penalty", "point", "what", "how",
            "explain", "when", "article", "drs", "safety"
        ]
        
        has_circuit = any(kw in query for kw in circuit_keywords)
        has_regulations = any(kw in query for kw in regulations_keywords)
        
        # Check for circuit location mentions
        circuit_locations = [
            loc.lower().replace('_', ' ')
            for loc in self.circuit_tool.CIRCUIT_LOCATIONS
        ]
        has_location = any(loc in query for loc in circuit_locations)
        
        if has_circuit or has_location:
            intent = "both" if has_regulations else "circuit"
        elif has_regulations:
            intent = "regulations"
        else:
            intent = "regulations"  # Default
        
        logger.info(f"Intent classified as: {intent}")
        state["intent"] = intent
        state["messages"].append(SystemMessage(content=f"Intent: {intent}"))
        
        return state

    def route_query(
        self, state: AgentState
    ) -> Literal["circuit", "regulations", "both", "unknown"]:
        """Route based on classified intent."""
        return state["intent"]

    @traceable(name="execute_circuit", tags=["orchestrator", "circuit"])
    def execute_circuit(self, state: AgentState) -> AgentState:
        """Execute circuit image retrieval."""
        logger.info("Executing circuit retrieval")
        
        try:
            result = self.circuit_tool.get_circuit_image(state["query"])
            state["circuit_result"] = result
            logger.info(f"Circuit status: {result.get('metadata', {}).get('status')}")
        except Exception as e:
            logger.error(f"Circuit retrieval failed: {e}")
            state["circuit_result"] = {
                "type": "error",
                "content": str(e),
                "metadata": {"error": str(e)}
            }
        
        return state

    @traceable(name="execute_regulations", tags=["orchestrator", "regulations"])
    def execute_regulations(self, state: AgentState) -> AgentState:
        """Execute regulations RAG query."""
        logger.info("Executing regulations RAG")
        
        try:
            result = self.regulations_tool.query_regulations(state["query"])
            state["regulations_result"] = result
            logger.info(f"Regulations status: {result.get('metadata', {}).get('status')}")
        except Exception as e:
            logger.error(f"Regulations query failed: {e}")
            state["regulations_result"] = {
                "type": "error",
                "content": str(e),
                "metadata": {"error": str(e)}
            }
        
        return state

    @traceable(name="synthesize_response", tags=["orchestrator", "synthesis"])
    def synthesize_response(self, state: AgentState) -> AgentState:
        """Synthesize final response from tool results."""
        logger.info(f"Synthesizing response for intent: {state['intent']}")
        
        intent = state["intent"]
        
        if intent == "circuit":
            result = state.get("circuit_result", {})
            if result.get("type") == "image":
                state["final_response"] = {
                    "type": "image",
                    "content": result["content"],
                    "message": f"Circuit map: {result['metadata']['location']}",
                    "metadata": result["metadata"]
                }
            else:
                state["final_response"] = {
                    "type": "text",
                    "content": result.get("content", "Could not retrieve circuit."),
                    "metadata": result.get("metadata", {})
                }
        elif intent == "regulations":
            result = state.get("regulations_result", {})
            state["final_response"] = {
                "type": "text",
                "content": result.get("content", "No response generated."),
                "metadata": result.get("metadata", {})
            }
        elif intent == "both":
            state["final_response"] = {
                "type": "combined",
                "circuit": state.get("circuit_result", {}),
                "regulations": state.get("regulations_result", {}),
                "message": "Here's the information you requested:"
            }
        else:
            state["final_response"] = {
                "type": "text",
                "content": "I can help with F1 circuit maps or regulations questions."
            }
        
        return state

    @traceable(name="process_query", tags=["orchestrator", "main"])
    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Main entry point for processing user queries.
        
        Args:
            query: User's F1 query
            
        Returns:
            Response dict with results from appropriate tools
        """
        logger.info(f"Processing query: '{query}'")
        
        initial_state: AgentState = {
            "query": query,
            "intent": "",
            "circuit_result": {},
            "regulations_result": {},
            "final_response": "",
            "messages": [HumanMessage(content=query)]
        }
        
        try:
            final_state = self.app.invoke(initial_state)
            
            if final_state is None:
                logger.error("Graph returned None - this should not happen")
                return {
                    "query": query,
                    "intent": "error",
                    "response": {
                        "type": "error",
                        "content": "Internal error: graph execution failed"
                    },
                    "metadata": {
                        "circuit_executed": False,
                        "regulations_executed": False,
                        "error": "Graph returned None"
                    }
                }
            
            logger.success("Query processing complete")
            
            return {
                "query": query,
                "intent": final_state["intent"],
                "response": final_state["final_response"],
                "metadata": {
                    "circuit_executed": bool(final_state.get("circuit_result")),
                    "regulations_executed": bool(final_state.get("regulations_result"))
                }
            }
        except Exception as e:
            logger.error(f"Error during query processing: {e}")
            import traceback
            traceback.print_exc()
            return {
                "query": query,
                "intent": "error",
                "response": {
                    "type": "error",
                    "content": f"Error processing query: {str(e)}"
                },
                "metadata": {
                    "circuit_executed": False,
                    "regulations_executed": False,
                    "error": str(e)
                }
            }


# Singleton
_orchestrator_instance = None


def get_orchestrator() -> F1AgentOrchestrator:
    """Get or create singleton instance."""
    global _orchestrator_instance
    
    if _orchestrator_instance is None:
        _orchestrator_instance = F1AgentOrchestrator()
    
    return _orchestrator_instance
