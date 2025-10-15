"""Data Dependence Graph (DDG) for PyFlow.

This package provides data dependence graph construction on top of the
existing dataflowIR and SSA infrastructure. It exposes a small API:

- DDG node/edge/graph data structures (see graph.py)
- DDG construction from dataflowIR graphs (see construction.py)
- Dump utilities for text/DOT/JSON (see dump.py)
"""

from .graph import DataDependenceGraph, DDGNode, DDGEdge
from .construction import construct_ddg, DDGConstructor
from .dump import dump_ddg, DDGDumper, dump_ddg_to_directory

__all__ = [
    "DataDependenceGraph",
    "DDGNode",
    "DDGEdge",
    "DDGConstructor",
    "construct_ddg",
    "DDGDumper",
    "dump_ddg",
    "dump_ddg_to_directory",
]


