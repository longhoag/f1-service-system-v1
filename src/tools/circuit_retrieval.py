"""
Circuit image retrieval tool.
Simplified for GPT-5 Mini agent - no hardcoded aliases.
GPT-5 Mini understands location queries naturally.
Uses LangSmith for tracing.
"""

from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger
from langsmith import traceable


class CircuitRetrieval:
    """
    Tool for retrieving F1 circuit images from the f1_2025_circuit_maps directory.
    
    Designed for GPT-5 Mini agent with tool calling.
    No hardcoded aliases - agent understands locations naturally.
    """

    # Available circuit locations for 2025 season (24 circuits)
    CIRCUIT_LOCATIONS = [
        "Abu_Dhabi", "Australia", "Austria", "Bahrain", "Baku", "Belgium",
        "Brazil", "Canada", "China", "Emilia_Romagna", "Great_Britain",
        "Hungary", "Italy", "Japan", "Las_Vegas", "Mexico", "Miami",
        "Monaco", "Netherlands", "Qatar", "Saudi_Arabia", "Singapore",
        "Spain", "USA"
    ]

    def __init__(self, circuit_maps_dir: str = "f1_2025_circuit_maps"):
        """
        Initialize circuit retrieval tool.
        
        Args:
            circuit_maps_dir: Path to directory containing circuit images
        """
        # Get absolute path from project root
        base_dir = Path(__file__).parent.parent.parent
        self.circuit_maps_dir = base_dir / circuit_maps_dir
        
        if not self.circuit_maps_dir.exists():
            logger.warning(f"Circuit maps directory not found: {self.circuit_maps_dir}")
        else:
            logger.success(f"Circuit maps directory: {self.circuit_maps_dir}")

    @traceable(name="get_circuit_image", tags=["circuit", "retrieval"])
    def get_circuit_image(self, location: str) -> Dict[str, Any]:
        """
        Retrieve circuit image path based on location.
        
        Simplified for GPT-5 Mini agent - just maps location to file.
        GPT-5 Mini handles query understanding and provides normalized location.
        
        Args:
            location: Circuit location (e.g., "Monaco", "Las Vegas", "Great Britain")
            
        Returns:
            Dict with type, content (path), and metadata
        """
        logger.info(f"Retrieving circuit image for: '{location}'")
        
        # Normalize location name to match file convention
        normalized = self._normalize_location(location)
        
        if not normalized:
            logger.warning(f"Location not found: '{location}'")
            return {
                "type": "error",
                "content": (
                    f"Circuit '{location}' not found. "
                    f"Available circuits: {', '.join(self.CIRCUIT_LOCATIONS)}"
                ),
                "metadata": {
                    "location": location,
                    "status": "not_found",
                    "available_circuits": self.CIRCUIT_LOCATIONS
                }
            }
        
        # Build image path
        image_filename = f"{normalized}_Circuit.webp"
        image_path = self.circuit_maps_dir / image_filename
        
        if not image_path.exists():
            logger.error(f"Circuit image file not found: {image_path}")
            return {
                "type": "error",
                "content": f"Found circuit '{normalized}' but image file is missing.",
                "metadata": {
                    "location": location,
                    "normalized": normalized,
                    "expected_file": image_filename,
                    "status": "file_missing"
                }
            }
        
        logger.success(f"Circuit image found: {normalized} -> {image_filename}")
        
        return {
            "type": "image",
            "content": str(image_path.absolute()),
            "metadata": {
                "location": location,
                "normalized": normalized,
                "filename": image_filename,
                "status": "success"
            }
        }

    @traceable(name="normalize_location", tags=["processing"])
    def _normalize_location(self, location: str) -> Optional[str]:
        """
        Normalize location to match file naming convention.
        
        Simplified - just matches against official names.
        GPT-5 Mini should provide reasonably normalized names.
        
        Args:
            location: Location string from GPT-5 Mini
            
        Returns:
            Normalized location name or None
        """
        location_lower = location.lower().strip()
        
        # Direct match against official names
        for circuit_name in self.CIRCUIT_LOCATIONS:
            circuit_lower = circuit_name.lower().replace('_', ' ')
            
            # Exact match
            if location_lower == circuit_lower:
                logger.debug(f"Exact match: '{location}' -> '{circuit_name}'")
                return circuit_name
            
            # Location is contained in circuit name
            if location_lower in circuit_lower:
                logger.debug(f"Partial match: '{location}' -> '{circuit_name}'")
                return circuit_name
            
            # Circuit name parts in location (handles "Vegas" -> "Las_Vegas")
            circuit_parts = circuit_lower.split()
            if any(part in location_lower for part in circuit_parts if len(part) > 3):
                logger.debug(f"Part match: '{location}' -> '{circuit_name}'")
                return circuit_name
        
        logger.warning(f"No match found for: '{location}'")
        return None

    def list_available_circuits(self) -> list:
        """Return list of all available circuit locations."""
        return self.CIRCUIT_LOCATIONS.copy()


# Singleton instance
_circuit_retrieval_instance: Optional[CircuitRetrieval] = None


def get_circuit_retrieval() -> CircuitRetrieval:
    """Get or create singleton instance of CircuitRetrieval."""
    global _circuit_retrieval_instance
    
    if _circuit_retrieval_instance is None:
        _circuit_retrieval_instance = CircuitRetrieval()
    
    return _circuit_retrieval_instance
