"""
Constraint-based call graph extraction.

This package implements a lightweight constraint-based algorithm that
over-approximates potential call relationships using simple points-to style
constraints over function values. It aims to be more expressive than the
basic AST walker without depending on external libraries.

Supports both single-file and multi-module analysis.
"""

from .builder import extract_call_graph_constraint, analyze_file_constraint

__all__ = [
    "extract_call_graph_constraint",
    "analyze_file_constraint",
]


