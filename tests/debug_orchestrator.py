"""Simple test to debug the orchestrator graph execution"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.logger import setup_logger
from loguru import logger

setup_logger()

logger.info("Testing orchestrator initialization...")

try:
    from src.agents.orchestrator import get_orchestrator
    logger.info("✓ Import successful")
    
    orchestrator = get_orchestrator()
    logger.info("✓ Orchestrator initialized")
    
    logger.info(f"Orchestrator type: {type(orchestrator)}")
    logger.info(f"Has app attr: {hasattr(orchestrator, 'app')}")
    logger.info(f"App type: {type(orchestrator.app)}")
    
    # Test simple query
    logger.info("\n" + "="*70)
    logger.info("Testing simple query...")
    logger.info("="*70)
    
    result = orchestrator.process_query("Show me Monaco")
    
    logger.info(f"Result type: {type(result)}")
    logger.info(f"Result: {result}")
    
except Exception as e:
    logger.error(f"Error: {e}")
    import traceback
    traceback.print_exc()
