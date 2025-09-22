"""
A call graph depicts calling relationships between subroutines in a computer program.
It is an essential component in most static analysis and can be leveraged to build more sophisicated applications such as profiling, vunerability propagation and refactoring.

This module provides call graph extraction capabilities with multiple algorithms
to choose from, allowing users to select the most appropriate one for their needs.
"""

# Import algorithm components
from .algorithms import CallGraphData, CallGraphAlgorithm, AlgorithmRegistry
from .algorithms.registry import registry

# Import specific algorithms
from .algorithms.ast_based import ASTBasedAlgorithm
try:
    from .algorithms.pycg_based import PyCGBasedAlgorithm
    PYCG_AVAILABLE = True
except ImportError:
    PYCG_AVAILABLE = False

# Import utilities
from .formats import generate_dot_output, generate_json_output, generate_text_output
from .cli import run_callgraph, add_callgraph_parser

__all__ = [
    # Core components
    "CallGraphData",
    "CallGraphAlgorithm", 
    "AlgorithmRegistry",
    "registry",
    
    # Algorithms
    "ASTBasedAlgorithm",
    
    # PyCG algorithm (if available)
    *(["PyCGBasedAlgorithm"] if PYCG_AVAILABLE else []),
    
    # Utilities
    "generate_dot_output",
    "generate_json_output", 
    "generate_text_output",
    "run_callgraph",
    "add_callgraph_parser",
]
