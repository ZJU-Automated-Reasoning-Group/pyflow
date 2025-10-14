"""Control Flow Graph Intermediate Representation (CFG-IR) for PyFlow.

This package provides an intermediate representation based on control flow graphs
that is used for data flow analysis and synthesis. It includes CFG node definitions,
structural analysis, and data flow synthesis capabilities.

The CFG-IR differs from the main CFG module by focusing on intermediate
representations that bridge between AST and data flow analysis, enabling
more sophisticated program transformations and optimizations.
"""

from . import cfg, dataflowsynthesis, dumpcfgir, structuralanalysis
