"""Analysis pipeline for PyFlow static analysis.

This module defines the main analysis pipeline that orchestrates various
static analysis passes including inter-procedural analysis, constraint-based
analysis, and optimization passes.

The pipeline now supports both the legacy hardcoded pipeline and the new
pass manager system for better modularity and extensibility.
"""

import time
import pyflow.util as util

# Import analysis modules (for legacy compatibility)
from pyflow.analysis import ipa
from pyflow.analysis import cpa
from pyflow.analysis import lifetimeanalysis
from pyflow.analysis.dump import dumpreport
from pyflow.analysis import programculler

# Import optimization modules (for legacy compatibility)
from pyflow.optimization import methodcall
from pyflow.optimization import cullprogram
from pyflow.optimization import simplify
from pyflow.optimization import clone
from pyflow.optimization import argumentnormalization
from pyflow.optimization import codeinlining
from pyflow.optimization import loadelimination
from pyflow.optimization import storeelimination
from pyflow.optimization import dce

# Import stats module
from .. import stats
from .. import config
import threading

from . import errors
from .passmanager import PassManager, PassPipeline
from .passes import register_standard_passes


class Pipeline(object):
    """Main analysis pipeline for PyFlow static analysis.

    The Pipeline class orchestrates the execution of various analysis passes
    including inter-procedural analysis, constraint-based analysis, and
    optimization passes on Python programs.

    Supports both legacy hardcoded pipelines and the new pass manager system.
    """

    def __init__(self, use_pass_manager: bool = True):
        """Initialize the analysis pipeline.

        Args:
            use_pass_manager: Whether to use the new pass manager system.
                             If False, falls back to legacy hardcoded pipeline.
        """
        self.use_pass_manager = use_pass_manager
        self.pass_manager = None

        if use_pass_manager:
            self.pass_manager = PassManager()
            register_standard_passes(self.pass_manager)

    def run(self, program, compiler=None, name: str = "main"):
        """Run the analysis pipeline on a program.

        Args:
            program: Program object to analyze.
            compiler: Compiler instance (required for pass manager).
            name: Name for the analysis run (for logging/debugging).

        Returns:
            Dict of pass results if using pass manager, None otherwise.
        """
        if self.use_pass_manager:
            if compiler is None:
                raise ValueError("Compiler instance required when using pass manager")
            return self._run_with_pass_manager(compiler, program, name)
        else:
            return self._run_legacy_pipeline(compiler, program, name)

    def _run_with_pass_manager(self, compiler, program, name: str):
        """Run pipeline using the pass manager system."""
        if not self.pass_manager:
            raise RuntimeError("Pass manager not initialized")

        # Build a comprehensive pipeline
        pipeline = self.pass_manager.build_pipeline([
            "ipa",           # Inter-procedural analysis first
            "cpa",           # Constraint propagation analysis
            "lifetime",      # Lifetime analysis
            "methodcall",    # Method call optimization
            "simplify",      # Simplification (constant folding, DCE)
            "clone",         # Code cloning
            "argument_normalization",  # Argument normalization
            "cull_program",  # Program culling
            "store_elimination",       # Store elimination
        ])

        # Run the pipeline
        results = self.pass_manager.run_pipeline(compiler, program, pipeline)

        # Log execution summary
        successful = sum(1 for r in results.values() if r.success)
        total_time = sum(r.time for r in results.values() if hasattr(r, 'time'))

        print(f"Pass Manager: {successful}/{len(results)} passes successful in {total_time:.3f}s")

        return results

    def _run_legacy_pipeline(self, compiler, program, name: str):
        """Run the legacy hardcoded pipeline for backward compatibility."""
        return evaluate(compiler, program, name)

    # Convenience methods for pass manager operations
    def get_pass_manager(self) -> PassManager:
        """Get the pass manager instance."""
        if not self.use_pass_manager or not self.pass_manager:
            raise RuntimeError("Pass manager not enabled")
        return self.pass_manager

    def register_pass(self, pass_instance):
        """Register a custom pass with the pass manager."""
        if not self.use_pass_manager:
            raise RuntimeError("Pass manager not enabled")
        self.pass_manager.register_pass(pass_instance)

    def build_custom_pipeline(self, pass_names: list) -> PassPipeline:
        """Build a custom pipeline from pass names."""
        if not self.use_pass_manager:
            raise RuntimeError("Pass manager not enabled")
        return self.pass_manager.build_pipeline(pass_names)

    def run_custom_pipeline(self, compiler, program, pass_names: list):
        """Run a custom set of passes."""
        if not self.use_pass_manager:
            raise RuntimeError("Pass manager not enabled")
        pipeline = self.pass_manager.build_pipeline(pass_names)
        return self.pass_manager.run_pipeline(compiler, program, pipeline)

    def list_available_passes(self) -> list:
        """List all available passes."""
        if not self.use_pass_manager:
            return []
        return self.pass_manager.list_passes()

    def get_pass_info(self, pass_name: str):
        """Get metadata for a specific pass."""
        if not self.use_pass_manager:
            return None
        return self.pass_manager.get_pass_info(pass_name)

    def clear_cache(self):
        """Clear the pass manager cache."""
        if self.use_pass_manager and self.pass_manager:
            self.pass_manager.clear_cache()


def codeConditioning(compiler, prgm, firstPass, dumpStats=False):
    with compiler.console.scope("conditioning"):
        if firstPass:
            # Try to identify and optimize method calls
            methodcall.evaluate(compiler, prgm)

        lifetimeanalysis.evaluate(compiler, prgm)

        if True:
            # Fold, DCE, etc.
            simplify.evaluate(compiler, prgm)

        if firstPass and dumpStats:
            stats.contextStats(compiler, prgm, "optimized", classOK=True)

        if firstPass:
            # Separate different invocations of the same code.
            clone.evaluate(compiler, prgm)

        if firstPass and dumpStats:
            stats.contextStats(compiler, prgm, "clone", classOK=True)

        if firstPass:
            # Try to eliminate kwds, vargs, kargs, and default arguments.
            # Done before inlining, as the current implementation of inlining
            # Cannot deal with complex calling conventions.
            argumentnormalization.evaluate(compiler, prgm)

        if firstPass:
            # Try to eliminate trivial functions.
            # codeinlining.evaluate(compiler, prgm)  # Temporarily disabled

            # Get rid of dead functions/contexts
            cullprogram.evaluate(compiler, prgm)

        if False:  # Temporarily disable load elimination
            loadelimination.evaluate(compiler, prgm)


        if True:
            storeelimination.evaluate(compiler, prgm)

        # Summary of optimization phase
        compiler.console.output("Optimization phase completed")

        if firstPass and dumpStats:
            stats.contextStats(compiler, prgm, "inline")

        # HACK read/modify information is imprecise, so keep re-evaluating it
        # basically, DCE improves read modify information, which in turn allows better DCE
        # NOTE that this doesn't work very well without path sensitivity
        # "modifies" are quite imprecise without it, hence DCE doesn't do much.
        if False:  # Temporarily disable brute force simplification
            bruteForceSimplification(compiler, prgm)


def bruteForceSimplification(compiler, prgm):
    with compiler.console.scope("brute force"):
        for _i in range(2):
            lifetimeanalysis.evaluate(compiler, prgm)
            simplify.evaluate(compiler, prgm)


def depythonPass(compiler, prgm, opPathLength=0, firstPass=True):
    with compiler.console.scope("depython"):
        # Run IPA analysis and store results for later access
        ipa_result = ipa.evaluate(compiler, prgm)
        if ipa_result:
            prgm.ipa_analysis = ipa_result

        cpa.evaluate(compiler, prgm, opPathLength, firstPass=firstPass)

        if firstPass:
            stats.contextStats(
                compiler,
                prgm,
                "firstpass" if firstPass else "secondpass",
                classOK=firstPass,
            )
        # errors.abort("testing")

        codeConditioning(compiler, prgm, firstPass, firstPass)


def evaluate(compiler, prgm, name):
    try:
        with compiler.console.scope("compile"):
            try:
                # First compiler pass
                depythonPass(compiler, prgm)

                if True:
                    # Second compiler pass
                    # Intrinsics can prevent complete exhaustive inlining.
                    # Adding call-path sensitivity compensates.
                    depythonPass(compiler, prgm, 3, firstPass=False)
                else:
                    # HACK rerun lifetime analysis, as inlining causes problems for the function annotations.
                    lifetimeanalysis.evaluate(compiler, prgm)

                stats.contextStats(compiler, prgm, "secondpass")

                # errors.abort('test')

                # Translation phase removed - now a static analysis framework
            finally:
                if config.doDump:
                    try:
                        dumpreport.evaluate(compiler, prgm, name)
                    except Exception as e:
                        if config.maskDumpErrors:
                            # HACK prevents it from masking any exception that was thrown before.
                            print("Exception dumping the report: ", e)
                        else:
                            raise

                if config.doThreadCleanup:
                    if threading.activeCount() > 1:
                        with compiler.console.scope("threading cleanup"):
                            compiler.console.output(
                                "Threads: %d" % (threading.activeCount() - 1)
                            )
                            for t in threading.enumerate():
                                if t is not threading.currentThread():
                                    compiler.console.output(".")
                                    t.join()
    except errors.CompilerAbort as e:
        print()
        print("ABORT", e)
