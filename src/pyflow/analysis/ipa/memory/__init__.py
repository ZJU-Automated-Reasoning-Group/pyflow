"""IPA memory extraction policies.

This package provides memory extraction policies for Inter-procedural Analysis (IPA),
handling how object field values and type information are extracted during analysis.

Key components:
- ExtractorPolicy: Policy for extracting data from program objects
- StoreGraphPolicy: Policy for extracting data from store graph objects
- Field value extraction: Handles attribute and array access
- Type object extraction: Manages type information propagation

Memory policies enable IPA to handle different object representations
consistently across analysis contexts and calling conventions.
"""

from . import extractorpolicy, storegraphpolicy
