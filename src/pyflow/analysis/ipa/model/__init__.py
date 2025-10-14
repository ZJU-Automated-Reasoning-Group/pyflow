"""IPA analysis model classes.

This package provides the core model classes used by Inter-procedural Analysis (IPA)
to represent analysis contexts, function invocations, object regions, and naming.

Key components:
- Context: Analysis context representing function execution state
- Invocation: Function call invocation modeling
- Region: Memory region management for objects and slots
- ObjectName: Canonical naming for objects in analysis
- Object: Object representation in IPA analysis

These model classes form the foundation for IPA's context-sensitive
inter-procedural analysis, enabling precise tracking of object relationships
and data flow across function boundaries.
"""

from . import context, invocation, region, object, objectname
