"""
PyCG-based call graph extraction algorithm.

This algorithm uses the PyCG library for more sophisticated call graph analysis.
It can handle more complex Python constructs and provides better accuracy.
"""

from typing import Set, Dict, Any, Optional
import os

from .base import CallGraphAlgorithm, CallGraphData

try:
    import pycg  # type: ignore
    from pycg.pycg import CallGraphGenerator as CallGraphGeneratorPyCG  # type: ignore
    PYCG_AVAILABLE = True
except ImportError:
    PYCG_AVAILABLE = False


class PyCGBasedAlgorithm(CallGraphAlgorithm):
    """Extracts call graphs using the PyCG library."""

    def __init__(self, verbose: bool = False):
        super().__init__(verbose)
        if not PYCG_AVAILABLE:
            raise ImportError("PyCG library is not available. Install it with: pip install pycg")

    @property
    def name(self) -> str:
        return "pycg"

    @property
    def description(self) -> str:
        return "PyCG-based call graph extraction using the external PyCG library"

    def extract_from_program(self, program, compiler, args) -> CallGraphData:
        """Extract call graph from a pyflow program."""
        # For PyCG, we need to work with file paths
        if hasattr(compiler.extractor, 'source_file') and compiler.extractor.source_file:
            return self.extract_from_file(compiler.extractor.source_file, args)
        else:
            # Fallback to source code extraction
            return self.extract_from_source(compiler.extractor.source_code, args)

    def extract_from_source(self, source_code: str, args) -> CallGraphData:
        """Extract call graph directly from Python source code."""
        # PyCG works with files, so we need to create a temporary file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(source_code)
            temp_file = f.name
        
        try:
            return self.extract_from_file(temp_file, args)
        finally:
            os.unlink(temp_file)

    def extract_from_file(self, file_path: str, args) -> CallGraphData:
        """Extract call graph from a Python file using PyCG."""
        call_graph = CallGraphData()
        
        try:
            # Initialize PyCG generator
            generator = CallGraphGeneratorPyCG([file_path], os.path.dirname(file_path))
            
            generator.analyze()
            cg_data = generator.output()
            
            # Convert PyCG output to our CallGraphData format
            self._convert_pycg_to_callgraph_data(cg_data, call_graph)
            
        except Exception as e:
            if self.verbose:
                print(f"Error running PyCG: {e}")
        
        return call_graph

    def _convert_pycg_to_callgraph_data(self, cg_data: Dict[str, Set[str]], call_graph: CallGraphData):
        """Convert PyCG output format to CallGraphData."""
        # Create mock function objects for PyCG functions
        function_map = {}
        
        for func_name in cg_data.keys():
            class MockFunction:
                def __init__(self, name):
                    self.name = name
                    self.__name__ = name

                def codeName(self):
                    return self.name

            func = MockFunction(func_name)
            function_map[func_name] = func
            call_graph.functions.add(func)
            call_graph.invocations[func] = set()
            call_graph.function_contexts[func] = {None}

        # Add call relationships
        for caller_name, callees in cg_data.items():
            if caller_name in function_map:
                caller_func = function_map[caller_name]
                for callee_name in callees:
                    if callee_name in function_map:
                        call_graph.invocations[caller_func].add(function_map[callee_name])
                    else:
                        # Create a mock function for external calls
                        class MockExternalFunction:
                            def __init__(self, name):
                                self.name = name
                                self.__name__ = name

                            def codeName(self):
                                return self.name

                        external_func = MockExternalFunction(callee_name)
                        call_graph.functions.add(external_func)
                        call_graph.invocations[caller_func].add(external_func)
                        call_graph.function_contexts[external_func] = {None}
