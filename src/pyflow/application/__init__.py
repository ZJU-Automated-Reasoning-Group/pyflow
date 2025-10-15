"""
PyFlow Application Layer

This package contains the high-level application components for PyFlow,
including program representation, pipeline management, and error handling.

Now includes a LLVM-inspired pass manager system for flexible composition
and execution of analysis and optimization passes.
"""

from .program import Program
from .pipeline import Pipeline
from .context import Context
from .errors import CompilerAbort

# Pass manager system
from .passmanager import (
    PassManager, PassPipeline, Pass, PassResult, PassInfo,
    AnalysisPass, OptimizationPass, TransformationPass,
    PassKind, PassCache, create_analysis_pass, create_optimization_pass
)
from .passes import register_standard_passes

__all__ = [
    "Program", "Pipeline", "Context", "CompilerAbort",
    # Pass manager system
    "PassManager", "PassPipeline", "Pass", "PassResult", "PassInfo",
    "AnalysisPass", "OptimizationPass", "TransformationPass",
    "PassKind", "PassCache", "create_analysis_pass", "create_optimization_pass",
    "register_standard_passes"
]
