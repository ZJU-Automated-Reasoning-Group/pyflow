"""
Algorithm registry for managing available call graph algorithms.
"""

from typing import Dict, Type, List
from .base import CallGraphAlgorithm


class AlgorithmRegistry:
    """Registry for managing call graph algorithms."""

    def __init__(self):
        self._algorithms: Dict[str, Type[CallGraphAlgorithm]] = {}

    def register(self, algorithm_class: Type[CallGraphAlgorithm]):
        """Register a new algorithm."""
        self._algorithms[algorithm_class().name] = algorithm_class

    def get_algorithm(self, name: str) -> Type[CallGraphAlgorithm]:
        """Get an algorithm by name."""
        if name not in self._algorithms:
            raise ValueError(f"Unknown algorithm: {name}. Available: {list(self._algorithms.keys())}")
        return self._algorithms[name]

    def list_algorithms(self) -> List[str]:
        """List all available algorithm names."""
        return list(self._algorithms.keys())

    def get_algorithm_info(self, name: str) -> Dict[str, str]:
        """Get information about a specific algorithm."""
        if name not in self._algorithms:
            raise ValueError(f"Unknown algorithm: {name}")
        
        algorithm_class = self._algorithms[name]
        instance = algorithm_class()
        return {
            "name": instance.name,
            "description": instance.description
        }

    def list_all_info(self) -> Dict[str, Dict[str, str]]:
        """Get information about all algorithms."""
        return {name: self.get_algorithm_info(name) for name in self._algorithms}


# Global registry instance
registry = AlgorithmRegistry()

# Register default algorithms
from .ast_based import ASTBasedAlgorithm

registry.register(ASTBasedAlgorithm)

try:
    from .pycg_based import PyCGBasedAlgorithm, PYCG_AVAILABLE
    if PYCG_AVAILABLE:
        registry.register(PyCGBasedAlgorithm)
except ImportError:
    # PyCG not available, skip registration
    pass
