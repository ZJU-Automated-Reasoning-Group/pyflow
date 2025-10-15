"""
Standard pass implementations for PyFlow analysis and optimization.

This module provides wrapper passes for the existing PyFlow analysis and
optimization modules, allowing them to work with the new pass manager system.
"""

from .passmanager import AnalysisPass, OptimizationPass, PassResult
from pyflow.analysis import ipa, cpa, lifetimeanalysis
from pyflow.optimization import methodcall, simplify, clone, argumentnormalization, cullprogram, storeelimination


class IPAAnalysisPass(AnalysisPass):
    """Inter-procedural Analysis (IPA) pass."""

    def __init__(self):
        super().__init__("ipa", "Inter-procedural analysis for call graphs and contexts")

    def run(self, compiler, program) -> PassResult:
        try:
            result = ipa.evaluate(compiler, program)
            program.ipa_analysis = result
            return PassResult(success=True, changed=result is not None, data=result)
        except Exception as e:
            return PassResult(success=False, error=str(e))


class CPAAnalysisPass(AnalysisPass):
    """Constraint Propagation Analysis (CPA) pass."""

    def __init__(self):
        super().__init__("cpa", "Constraint-based analysis for type and flow constraints")

    def run(self, compiler, program) -> PassResult:
        try:
            # Run CPA with default parameters
            cpa_result = cpa.evaluate(compiler, program)
            return PassResult(success=True, changed=True, data=cpa_result)
        except Exception as e:
            return PassResult(success=False, error=str(e))


class LifetimeAnalysisPass(AnalysisPass):
    """Lifetime analysis pass for variable and object lifetimes."""

    def __init__(self):
        super().__init__("lifetime", "Analyzes lifetimes of variables and objects")

    def run(self, compiler, program) -> PassResult:
        try:
            lifetimeanalysis.evaluate(compiler, program)
            return PassResult(success=True, changed=True)
        except Exception as e:
            return PassResult(success=False, error=str(e))


class MethodCallOptimizationPass(OptimizationPass):
    """Method call optimization pass."""

    def __init__(self):
        super().__init__("methodcall", "Optimizes method calls and dispatch")

    def run(self, compiler, program) -> PassResult:
        try:
            methodcall.evaluate(compiler, program)
            return PassResult(success=True, changed=True)
        except Exception as e:
            return PassResult(success=False, error=str(e))


class SimplifyOptimizationPass(OptimizationPass):
    """Simplification pass for constant folding and DCE."""

    def __init__(self):
        super().__init__("simplify", "Constant folding, dead code elimination, and simplification")

    def run(self, compiler, program) -> PassResult:
        try:
            simplify.evaluate(compiler, program)
            return PassResult(success=True, changed=True)
        except Exception as e:
            return PassResult(success=False, error=str(e))


class CloneOptimizationPass(OptimizationPass):
    """Code cloning pass for separating different invocations."""

    def __init__(self):
        super().__init__("clone", "Separates different invocations of the same code")

    def run(self, compiler, program) -> PassResult:
        try:
            clone.evaluate(compiler, program)
            return PassResult(success=True, changed=True)
        except Exception as e:
            return PassResult(success=False, error=str(e))


class ArgumentNormalizationPass(OptimizationPass):
    """Argument normalization pass."""

    def __init__(self):
        super().__init__("argument_normalization", "Normalizes function arguments, eliminates *args, **kwargs")

    def run(self, compiler, program) -> PassResult:
        try:
            argumentnormalization.evaluate(compiler, program)
            return PassResult(success=True, changed=True)
        except Exception as e:
            return PassResult(success=False, error=str(e))


class ProgramCullingPass(OptimizationPass):
    """Program culling pass to remove dead functions/contexts."""

    def __init__(self):
        super().__init__("cull_program", "Removes dead functions and contexts")

    def run(self, compiler, program) -> PassResult:
        try:
            cullprogram.evaluate(compiler, program)
            return PassResult(success=True, changed=True)
        except Exception as e:
            return PassResult(success=False, error=str(e))


class StoreEliminationPass(OptimizationPass):
    """Store elimination pass."""

    def __init__(self):
        super().__init__("store_elimination", "Eliminates redundant store operations")

    def run(self, compiler, program) -> PassResult:
        try:
            storeelimination.evaluate(compiler, program)
            return PassResult(success=True, changed=True)
        except Exception as e:
            return PassResult(success=False, error=str(e))


# Registry of standard passes
STANDARD_PASSES = {
    "ipa": IPAAnalysisPass,
    "cpa": CPAAnalysisPass,
    "lifetime": LifetimeAnalysisPass,
    "methodcall": MethodCallOptimizationPass,
    "simplify": SimplifyOptimizationPass,
    "clone": CloneOptimizationPass,
    "argument_normalization": ArgumentNormalizationPass,
    "cull_program": ProgramCullingPass,
    "store_elimination": StoreEliminationPass,
}


def register_standard_passes(pass_manager):
    """Register all standard PyFlow passes with the pass manager."""
    for pass_name, pass_class in STANDARD_PASSES.items():
        pass_manager.register_pass(pass_class())

    # Set up dependencies based on the current hardcoded pipeline
    # IPA should run before CPA
    ipa_pass = pass_manager.passes["ipa"]
    cpa_pass = pass_manager.passes["cpa"]
    cpa_pass.info.dependencies.add("ipa")

    # CPA should run before most optimizations
    for opt_name in ["methodcall", "simplify", "clone", "argument_normalization", "cull_program"]:
        if opt_name in pass_manager.passes:
            opt_pass = pass_manager.passes[opt_name]
            opt_pass.info.dependencies.add("cpa")

    # Simplification should run before many other optimizations
    simplify_pass = pass_manager.passes["simplify"]
    for opt_name in ["clone", "argument_normalization", "cull_program"]:
        if opt_name in pass_manager.passes:
            opt_pass = pass_manager.passes[opt_name]
            opt_pass.info.dependencies.add("simplify")
