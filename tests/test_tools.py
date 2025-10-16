"""Test individual tool initialization"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.logger import setup_logger
from loguru import logger

setup_logger()

logger.info("Testing Circuit Retrieval Tool...")
try:
    from src.tools.circuit_retrieval import get_circuit_retrieval
    circuit_tool = get_circuit_retrieval()
    logger.success("✓ Circuit tool initialized")
    logger.info(f"Type: {type(circuit_tool)}")
except Exception as e:
    logger.error(f"✗ Circuit tool failed: {e}")
    import traceback
    traceback.print_exc()

logger.info("\nTesting Regulations RAG Tool...")
try:
    from src.tools.regulations_rag import get_regulations_rag
    rag_tool = get_regulations_rag()
    logger.success("✓ RAG tool initialized")
    logger.info(f"Type: {type(rag_tool)}")
except Exception as e:
    logger.error(f"✗ RAG tool failed: {e}")
    import traceback
    traceback.print_exc()
