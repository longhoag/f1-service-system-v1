"""Test LangGraph compilation directly"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.logger import setup_logger
from loguru import logger

setup_logger()

logger.info("Testing LangGraph import...")
try:
    from langgraph.graph import StateGraph, END
    logger.success("✓ LangGraph imported")
except Exception as e:
    logger.error(f"✗ LangGraph import failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

logger.info("\nTesting StateGraph creation...")
try:
    from typing import TypedDict, Annotated
    import operator
    
    class TestState(TypedDict):
        value: str
        messages: Annotated[list, operator.add]
    
    workflow = StateGraph(TestState)
    logger.success("✓ StateGraph created")
    
    logger.info("\nAdding test nodes...")
    
    def test_node(state):
        state["value"] = "test"
        return state
    
    workflow.add_node("test", test_node)
    workflow.set_entry_point("test")
    workflow.add_edge("test", END)
    
    logger.success("✓ Nodes added")
    
    logger.info("\nCompiling graph...")
    app = workflow.compile()
    logger.success("✓ Graph compiled")
    logger.info(f"App type: {type(app)}")
    
    logger.info("\nTesting invocation...")
    result = app.invoke({"value": "", "messages": []})
    logger.success(f"✓ Invoked successfully: {result}")
    
except Exception as e:
    logger.error(f"✗ Failed: {e}")
    import traceback
    traceback.print_exc()
