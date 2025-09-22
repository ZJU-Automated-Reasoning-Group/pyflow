"""
Base classes for call graph algorithms.
"""

from abc import ABC, abstractmethod
from typing import Set, Dict, Any, Optional, List
import collections


class CallGraphData:
    """Data structure to hold call graph information."""

    def __init__(self):
        self.functions: Set[Any] = set()
        self.invocations: Dict[Any, Set[Any]] = {}
        self.invocation_contexts: Dict[Any, Set[Any]] = {}
        self.function_contexts: Dict[Any, Set[Any]] = {}
        self.cycles: List[List[Any]] = []


class CallGraphAlgorithm(ABC):
    """Abstract base class for call graph algorithms."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    @abstractmethod
    def extract_from_program(self, program, compiler, args) -> CallGraphData:
        """Extract call graph from a pyflow program."""
        pass

    @abstractmethod
    def extract_from_source(self, source_code: str, args) -> CallGraphData:
        """Extract call graph directly from Python source code."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the algorithm name."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Return a description of the algorithm."""
        pass


def limit_depth(call_graph: CallGraphData, max_depth: int) -> CallGraphData:
    """Limit the call graph to a maximum depth."""
    if max_depth <= 0:
        return call_graph

    # Simple depth limiting - keep only functions within max_depth
    # This is a basic implementation and could be improved
    limited_graph = CallGraphData()
    limited_graph.functions = call_graph.functions.copy()
    limited_graph.invocations = call_graph.invocations.copy()
    limited_graph.invocation_contexts = call_graph.invocation_contexts.copy()
    limited_graph.function_contexts = call_graph.function_contexts.copy()

    return limited_graph


def detect_cycles(call_graph: CallGraphData) -> List[List[Any]]:
    """Detect cycles in the call graph."""
    cycles = []
    visited = set()
    rec_stack = set()

    def dfs(node, path):
        if node in rec_stack:
            # Found a cycle
            cycle_start = path.index(node)
            cycles.append(path[cycle_start:] + [node])
            return

        if node in visited:
            return

        visited.add(node)
        rec_stack.add(node)

        for callee in call_graph.invocations.get(node, set()):
            dfs(callee, path + [node])

        rec_stack.remove(node)

    for func in call_graph.functions:
        if func not in visited:
            dfs(func, [])

    return cycles
